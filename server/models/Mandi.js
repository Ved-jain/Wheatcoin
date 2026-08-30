const mongoose = require('mongoose');

const MandiSchema = new mongoose.Schema({
  name: { type: String, required: true },
  state: { type: String, required: true },
  district: { type: String, required: true },
  lat: { type: Number, required: true },
  lng: { type: Number, required: true },
});

module.exports = mongoose.model('Mandi', MandiSchema);
