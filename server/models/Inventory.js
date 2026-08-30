const mongoose = require('mongoose');

const InventorySchema = new mongoose.Schema({
  crop: { type: String, required: true },
  quantityQuintals: { type: Number, required: true },
  perishabilityIndex: { type: Number, required: true }, // 1 to 10 (1 = lasts forever, 10 = rots tomorrow)
  daysInStorage: { type: Number, default: 0 }
});

module.exports = mongoose.model('Inventory', InventorySchema);
