const mongoose = require('mongoose');

const CropPriceSchema = new mongoose.Schema({
  mandiId: { type: mongoose.Schema.Types.ObjectId, ref: 'Mandi', required: true },
  crop: { type: String, required: true },
  pricePerQuintal: { type: Number, required: true },
  date: { type: Date, default: Date.now },
  isAnomaly: { type: Boolean, default: false }, // To be updated by ML service later
});

module.exports = mongoose.model('CropPrice', CropPriceSchema);
