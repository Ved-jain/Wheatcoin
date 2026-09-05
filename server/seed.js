require('dotenv').config();
const mongoose = require('mongoose');
const Mandi = require('./models/Mandi');
const CropPrice = require('./models/CropPrice');
const Inventory = require('./models/Inventory');

const MONGO_URI = process.env.MONGO_URI || 'mongodb://localhost:27017/kisanmandi';

const seedData = async () => {
  try {
    await mongoose.connect(MONGO_URI);
    console.log('MongoDB Connected for seeding');

    // Clear existing data
    await Mandi.deleteMany({});
    await CropPrice.deleteMany({});
    await Inventory.deleteMany({});

    // 1. Insert 14 Real Indian APMC Mandis (with authentic GPS coordinates)
    const mandisData = [
      { name: "Azadpur Mandi", state: "Delhi", district: "North Delhi", lat: 28.7136, lng: 77.1780 },
      { name: "Ghazipur Mandi", state: "Delhi", district: "East Delhi", lat: 28.6256, lng: 77.3312 },
      { name: "Narela Mandi", state: "Delhi", district: "North West Delhi", lat: 28.8528, lng: 77.0911 },
      { name: "Okhla Mandi", state: "Delhi", district: "South East Delhi", lat: 28.5494, lng: 77.2736 },
      { name: "Najafgarh Mandi", state: "Delhi", district: "South West Delhi", lat: 28.6090, lng: 76.9855 },
      { name: "Karnal APMC Mandi", state: "Haryana", district: "Karnal", lat: 29.6857, lng: 76.9905 },
      { name: "Panipat Mandi", state: "Haryana", district: "Panipat", lat: 29.3909, lng: 76.9635 },
      { name: "Sonipat Mandi", state: "Haryana", district: "Sonipat", lat: 28.9931, lng: 77.0151 },
      { name: "Rohtak Grain Market", state: "Haryana", district: "Rohtak", lat: 28.8955, lng: 76.6066 },
      { name: "Meerut Mandi", state: "Uttar Pradesh", district: "Meerut", lat: 28.9845, lng: 77.7064 },
      { name: "Hapur Mandi", state: "Uttar Pradesh", district: "Hapur", lat: 28.7306, lng: 77.7759 },
      { name: "Bulandshahr Mandi", state: "Uttar Pradesh", district: "Bulandshahr", lat: 28.4070, lng: 77.8498 },
      { name: "Agra APMC Mandi", state: "Uttar Pradesh", district: "Agra", lat: 27.1767, lng: 78.0081 },
      { name: "Alwar Krishi Mandi", state: "Rajasthan", district: "Alwar", lat: 27.5530, lng: 76.6346 }
    ];

    const mandis = await Mandi.insertMany(mandisData);
    console.log(`Inserted ${mandis.length} real APMC mandis successfully.`);

    // 2. Realistic Price Matrix per Mandi for 5 Crops (INR / Quintal)
    // Realistic price variation reflecting regional demand, arrival volumes, and logistics
    const cropBaseRates = {
      Wheat:    [2250, 2220, 2380, 2260, 2340, 2420, 2390, 2310, 2360, 2290, 2320, 2270, 2240, 2300],
      Tomatoes: [3200, 3150, 2950, 3350, 3050, 2750, 2850, 3100, 2900, 3000, 2980, 2850, 2800, 2750],
      Potatoes: [1620, 1580, 1550, 1680, 1600, 1480, 1520, 1590, 1510, 1650, 1620, 1580, 1720, 1540],
      Onions:   [2350, 2400, 2250, 2480, 2300, 2150, 2200, 2320, 2220, 2280, 2260, 2190, 2150, 2120],
      Mustard:  [5550, 5480, 5620, 5520, 5580, 5680, 5600, 5540, 5650, 5450, 5480, 5420, 5380, 5720]
    };

    const prices = [];
    mandis.forEach((mandi, idx) => {
      for (const [cropName, rateList] of Object.entries(cropBaseRates)) {
        prices.push({
          mandiId: mandi._id,
          crop: cropName,
          pricePerQuintal: rateList[idx] || rateList[0],
          date: new Date()
        });
      }
    });

    await CropPrice.insertMany(prices);
    console.log(`Inserted ${prices.length} realistic crop-price records successfully.`);

    // 3. Realistic Farmer Inventory Portfolio
    const inventoryData = [
      { crop: "Tomatoes", quantityQuintals: 25, perishabilityIndex: 9, daysInStorage: 3 },
      { crop: "Wheat", quantityQuintals: 70, perishabilityIndex: 2, daysInStorage: 8 },
      { crop: "Potatoes", quantityQuintals: 45, perishabilityIndex: 4, daysInStorage: 12 },
      { crop: "Onions", quantityQuintals: 35, perishabilityIndex: 5, daysInStorage: 5 },
      { crop: "Mustard", quantityQuintals: 20, perishabilityIndex: 2, daysInStorage: 6 }
    ];

    await Inventory.insertMany(inventoryData);
    console.log(`Inserted ${inventoryData.length} farmer inventory assets successfully.`);

    console.log('Seeding completed successfully!');
    process.exit(0);
  } catch (err) {
    console.error('Error seeding data:', err);
    process.exit(1);
  }
};

seedData();
