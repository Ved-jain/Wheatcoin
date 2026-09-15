const express = require('express');
const router = express.Router();
const path = require('path');
const fs = require('fs');
const Mandi = require('../models/Mandi');
const CropPrice = require('../models/CropPrice');
const Inventory = require('../models/Inventory');
const { calculateNetEarning, getDistanceKm, calculateFreshnessAdjustedProfit } = require('../utils/mathLogic');

const ML_SERVICE_URL = process.env.ML_SERVICE_URL || 'http://127.0.0.1:8000';

// Portfolio endpoint
router.get('/portfolio', async (req, res) => {
  try {
    const inventoryItems = await Inventory.find({});
    const portfolio = [];
    let totalValue = 0;

    for (const item of inventoryItems) {
      // Find the highest price currently available for this crop
      const prices = await CropPrice.find({ crop: item.crop }).sort({ pricePerQuintal: -1 });
      const bestPrice = prices.length > 0 ? prices[0].pricePerQuintal : 0;
      
      const value = item.quantityQuintals * bestPrice;
      totalValue += value;

      portfolio.push({
        crop: item.crop,
        quantity: item.quantityQuintals,
        perishabilityIndex: item.perishabilityIndex,
        daysInStorage: item.daysInStorage,
        currentMarketRate: bestPrice,
        totalValue: value
      });
    }

    res.json({
      totalValue,
      assets: portfolio
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Add new stock to portfolio
router.post('/portfolio', async (req, res) => {
  try {
    const { crop, quantityQuintals, perishabilityIndex, daysInStorage } = req.body;
    
    let item = await Inventory.findOne({ crop });
    if (item) {
      item.quantityQuintals += parseFloat(quantityQuintals);
      item.perishabilityIndex = parseInt(perishabilityIndex) || item.perishabilityIndex;
      item.daysInStorage = parseInt(daysInStorage) || item.daysInStorage;
      await item.save();
    } else {
      item = new Inventory({
        crop,
        quantityQuintals: parseFloat(quantityQuintals),
        perishabilityIndex: parseInt(perishabilityIndex) || 5,
        daysInStorage: parseInt(daysInStorage) || 0
      });
      await item.save();
    }
    res.json({ success: true, item });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Get prices with AI insights & confidence scores
router.get('/prices', async (req, res) => {
  try {
    const userLat = parseFloat(req.query.lat) || 28.6139; // Default: Delhi NCR
    const userLng = parseFloat(req.query.lng) || 77.2090;
    const cropQuery = req.query.crop || "Tomatoes";
    
    const inv = await Inventory.findOne({ crop: cropQuery });
    const perishability = inv ? inv.perishabilityIndex : 5;
    const daysInStorage = inv ? inv.daysInStorage : 0;

    const mandis = await Mandi.find({});
    const mandiPrices = [];
    
    for (const m of mandis) {
      const priceDoc = await CropPrice.findOne({ mandiId: m._id, crop: cropQuery }).sort({ date: -1 });
      if (priceDoc) {
        mandiPrices.push({
          mandiName: m.name,
          state: m.state,
          district: m.district,
          crop: priceDoc.crop,
          grossPrice: priceDoc.pricePerQuintal,
          lat: m.lat,
          lng: m.lng
        });
      }
    }

    const results = [];
    const fetchFn = globalThis.fetch;

    for (const item of mandiPrices) {
      const distance = getDistanceKm(userLat, userLng, item.lat, item.lng);
      const baseNet = calculateNetEarning(item.grossPrice, distance);
      const trueProfit = calculateFreshnessAdjustedProfit(baseNet, perishability, daysInStorage);
      
      let recommendation = 'HOLD';
      let confidence = 0.85;
      let confidencePct = 85.0;
      let reasoning = 'Awaiting AI decision...';
      let probabilities = { HOLD: 0.33, 'SELL 50%': 0.33, 'SELL 100%': 0.34 };

      let sellPercentage = 0;
      let copilotTip = '';
      let urgency = 'MEDIUM';
      let copilotEnabled = false;

      try {
        const aiResponse = await fetchFn(`${ML_SERVICE_URL}/predict_action`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            net_earning: trueProfit, 
            distance_km: distance,
            perishability: perishability,
            days_in_storage: daysInStorage,
            crop_name: item.crop,
            mandi_name: item.mandiName
          })
        });
        
        if (aiResponse.ok) {
          const aiData = await aiResponse.json();
          recommendation = aiData.recommendation || recommendation;
          confidence = aiData.confidence || confidence;
          confidencePct = aiData.confidence_pct || confidencePct;
          reasoning = aiData.reasoning || reasoning;
          probabilities = aiData.probabilities || probabilities;
          sellPercentage = aiData.sell_percentage !== undefined ? aiData.sell_percentage : (recommendation.includes('100%') ? 100 : recommendation.includes('50%') ? 50 : 0);
          copilotTip = aiData.copilot_tip || reasoning;
          urgency = aiData.urgency || 'MEDIUM';
          copilotEnabled = aiData.copilot_enabled || false;
        }
      } catch (e) {
        // Fallback rule if ML microservice is temporarily offline
        if (perishability >= 8 && daysInStorage >= 3) {
          recommendation = 'SELL 100%';
          sellPercentage = 100;
          reasoning = 'Urgent: High perishability crop reaching shelf-life limit.';
        } else if (trueProfit > 2400) {
          recommendation = 'SELL 50%';
          sellPercentage = 50;
          reasoning = 'Favorable price margin. Liquidate partial batch to hedge.';
        } else {
          recommendation = 'HOLD';
          sellPercentage = 0;
          reasoning = 'Low net margin after transport deduction. Retain stock.';
        }
        copilotTip = reasoning;
      }

      results.push({
        ...item,
        distanceKm: distance.toFixed(1),
        netEarning: trueProfit.toFixed(2),
        baseNetEarning: baseNet.toFixed(2),
        recommendation,
        confidence,
        confidencePct,
        probabilities,
        reasoning,
        sellPercentage,
        copilotTip,
        urgency,
        copilotEnabled
      });
    }

    results.sort((a, b) => b.netEarning - a.netEarning);
    res.json(results);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Model metrics proxy endpoint
router.get('/model-metrics', async (req, res) => {
  try {
    const fetchFn = globalThis.fetch;
    const aiResponse = await fetchFn(`${ML_SERVICE_URL}/model_metrics`);
    if (aiResponse.ok) {
      const data = await aiResponse.json();
      return res.json(data);
    }
  } catch (e) {
    console.warn("Could not reach ML service for metrics, attempting local fallback file...");
  }

  // Fallback to local metrics file if accessible
  const fallbackPath = path.resolve(__dirname, '../../ml_service/models/model_metrics.json');
  if (fs.existsSync(fallbackPath)) {
    try {
      const data = JSON.parse(fs.readFileSync(fallbackPath, 'utf8'));
      return res.json(data);
    } catch (err) {
      return res.status(500).json({ error: "Failed to read metrics file" });
    }
  }

  res.status(503).json({ error: "ML metrics currently unavailable. Start ml_service." });
});

module.exports = router;
