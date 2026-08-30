const express = require('express');
const router = express.Router();
const Mandi = require('../models/Mandi');
const CropPrice = require('../models/CropPrice');
const Inventory = require('../models/Inventory');
const { calculateNetEarning, getDistanceKm, calculateFreshnessAdjustedProfit } = require('../utils/mathLogic');

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

// Get prices with AI insights
router.get('/prices', async (req, res) => {
  try {
    const userLat = parseFloat(req.query.lat) || 28.6139;
    const userLng = parseFloat(req.query.lng) || 77.2090;
    
    // We assume the user is querying for a specific crop, e.g. Tomatoes
    const cropQuery = req.query.crop || "Tomatoes";
    
    // Find perishability index from inventory (mocking this connection for simplicity)
    const inv = await Inventory.findOne({ crop: cropQuery });
    const perishability = inv ? inv.perishabilityIndex : 5;
    const daysInStorage = inv ? inv.daysInStorage : 0;

    const mandis = await Mandi.find({});
    const dummyPrices = [];
    
    for (const m of mandis) {
      const priceDoc = await CropPrice.findOne({ mandiId: m._id, crop: cropQuery }).sort({ date: -1 });
      if (priceDoc) {
        dummyPrices.push({
          mandiName: m.name,
          crop: priceDoc.crop,
          grossPrice: priceDoc.pricePerQuintal,
          lat: m.lat,
          lng: m.lng
        });
      }
    }

    const results = [];
    for (const item of dummyPrices) {
      const distance = getDistanceKm(userLat, userLng, item.lat, item.lng);
      
      // Basic math
      const baseNet = calculateNetEarning(item.grossPrice, distance);
      // Sweet spot algorithm
      const trueProfit = calculateFreshnessAdjustedProfit(baseNet, perishability, daysInStorage);
      
      let recommendation = 'HOLD';
      let reasoning = 'Awaiting AI decision...';

      try {
        const fetch = (await import('node-fetch')).default || global.fetch; // compatibility fallback
        const aiResponse = await fetch('http://127.0.0.1:8000/predict_action', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            net_earning: trueProfit, 
            distance_km: distance,
            perishability: perishability
          })
        });
        
        if (aiResponse.ok) {
          const aiData = await aiResponse.json();
          recommendation = aiData.recommendation || recommendation;
          reasoning = aiData.reasoning || reasoning;
        }
      } catch (e) {
        console.error("AI service error:", e.message);
      }

      results.push({
        ...item,
        distanceKm: distance.toFixed(1),
        netEarning: trueProfit.toFixed(2),
        baseNetEarning: baseNet.toFixed(2),
        recommendation,
        reasoning
      });
    }

    results.sort((a, b) => b.netEarning - a.netEarning);
    res.json(results);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;
