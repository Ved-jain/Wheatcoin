require('dotenv').config();
const express = require('express');
const cors = require('cors');
const mongoose = require('mongoose');

const app = express();
const port = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

// MongoDB connection
mongoose.connect(process.env.MONGO_URI || 'mongodb://localhost:27017/kisanmandi')
  .then(() => console.log('MongoDB Connected'))
  .catch(err => console.log(err));

app.use('/api', require('./routes/api'));

app.get('/', (req, res) => {
  res.send('KisanMandi API is running');
});

app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
