/**
 * Calculates Net Earning
 * Net Earning = Gross Price - (Distance * Transport Cost per km) - Commission
 */
function calculateNetEarning(pricePerQuintal, distanceKm, transportRatePerKm = 5, commissionRate = 0.02) {
  const transportCost = distanceKm * transportRatePerKm;
  const commissionCost = pricePerQuintal * commissionRate;
  const netEarning = pricePerQuintal - transportCost - commissionCost;
  return netEarning > 0 ? netEarning : 0;
}

/**
 * Calculates Inverse Distance Weighting (IDW) to estimate price
 * @param {Array} knownPrices - Array of { price, distance }
 */
function calculateIDW(knownPrices) {
  let numerator = 0;
  let denominator = 0;

  for (const kp of knownPrices) {
    if (kp.distance === 0) return kp.price; // exact match
    const weight = 1 / Math.pow(kp.distance, 2);
    numerator += kp.price * weight;
    denominator += weight;
  }

  if (denominator === 0) return 0;
  return Math.round(numerator / denominator);
}

// Simple Haversine formula to calculate distance between lat/lng
function getDistanceKm(lat1, lon1, lat2, lon2) {
  const R = 6371; // Radius of the earth in km
  const dLat = deg2rad(lat2 - lat1);
  const dLon = deg2rad(lon2 - lon1); 
  const a = 
    Math.sin(dLat/2) * Math.sin(dLat/2) +
    Math.cos(deg2rad(lat1)) * Math.cos(deg2rad(lat2)) * 
    Math.sin(dLon/2) * Math.sin(dLon/2); 
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a)); 
  const d = R * c;
  return d;
}

function deg2rad(deg) {
  return deg * (Math.PI/180);
}

/**
 * Calculates True Profit by taking Freshness Decay into account.
 * Perishability Index (1-10) where 10 decays 5% value per day, 1 decays 0.5% per day.
 */
function calculateFreshnessAdjustedProfit(netEarning, perishabilityIndex, daysInStorage) {
  const decayRatePerDay = perishabilityIndex * 0.005; // 10 -> 5%, 1 -> 0.5%
  const totalDecay = decayRatePerDay * daysInStorage;
  if (totalDecay >= 1) return 0;
  return netEarning * (1 - totalDecay);
}

module.exports = {
  calculateNetEarning,
  calculateIDW,
  getDistanceKm,
  calculateFreshnessAdjustedProfit
};
