require('dotenv').config();
const mongoose = require('mongoose');
const Mandi = require('./models/Mandi');
const CropPrice = require('./models/CropPrice');

const MONGO_URI = process.env.MONGO_URI || 'mongodb://localhost:27017/kisanmandi';

const seedData = async () => {
  try {
    await mongoose.connect(MONGO_URI);
    console.log('MongoDB Connected for seeding');

    const Inventory = require('./models/Inventory');

    // Clear existing data
    await Mandi.deleteMany({});
    await CropPrice.deleteMany({});
    await Inventory.deleteMany({});

    // 1. Insert Mandis
    const mandis = await Mandi.insertMany([
      { name: "Azadpur Mandi", state: "Delhi", district: "North Delhi", lat: 28.7360, lng: 77.1724 },
      { name: "Narela Mandi", state: "Delhi", district: "North West Delhi", lat: 28.8428, lng: 77.0911 },
      { name: "Najafgarh Mandi", state: "Delhi", district: "South West Delhi", lat: 28.6090, lng: 76.9855 },
      { name: "Okhla Mandi", state: "Delhi", district: "South East Delhi", lat: 28.5494, lng: 77.2736 }
    ]);

    console.log('Mandis seeded successfully');

    // 2. Insert Crop Prices for these mandis
    const prices = [];
    const wheatBasePrices = [2200, 2350, 2100, 2050];
    const tomatoBasePrices = [3000, 2800, 3200, 3100]; // Tomatoes are more expensive but highly perishable

    for (let i = 0; i < mandis.length; i++) {
      prices.push({
        mandiId: mandis[i]._id,
        crop: "Wheat",
        pricePerQuintal: wheatBasePrices[i]
      });
      prices.push({
        mandiId: mandis[i]._id,
        crop: "Tomatoes",
        pricePerQuintal: tomatoBasePrices[i]
      });
    }

    await CropPrice.insertMany(prices);
    console.log('CropPrices seeded successfully');

    // 3. Insert Farmer Inventory Portfolio
    await Inventory.insertMany([
      { crop: "Wheat", quantityQuintals: 50, perishabilityIndex: 2, daysInStorage: 10 },
      { crop: "Tomatoes", quantityQuintals: 20, perishabilityIndex: 9, daysInStorage: 4 }
    ]);
    console.log('Inventory Portfolio seeded successfully');

    process.exit(0);
  } catch (err) {
    console.error('Error seeding data:', err);
    process.exit(1);
  }
};

seedData();
