"""
Liquidation Decision Policy & Ground-Truth Action Formulator
============================================================
Formulates actionable multi-class recommendations:
  0 = HOLD       (Depressed spot price, safe shelf-life remaining)
  1 = SELL 50%   (Balanced margin, staggered cash flow hedging)
  2 = SELL 100%  (Imminent spoilage hazard or peak windfall arbitrage)
"""

def determine_ground_truth_action(gross_price: float, baseline_price: float, 
                                  freshness_adjusted_net: float,
                                  perishability: int, days_in_storage: int, 
                                  max_safe_days: int) -> int:
    """
    Evaluates agricultural market utility to determine ground truth action label.
    """
    shelf_life_used_ratio = days_in_storage / float(max_safe_days)
    premium_pct = round(float(((gross_price - baseline_price) / baseline_price) * 100.0), 1)
    
    # Policy Rule 1: Imminent Spoilage -> Liquidate 100%
    if (perishability >= 8 and days_in_storage >= 3) or shelf_life_used_ratio >= 0.70:
        return 2  # SELL 100%
        
    # Policy Rule 2: Peak Market Windfall -> Liquidate 100%
    if premium_pct >= 10.0 and freshness_adjusted_net >= baseline_price:
        return 2  # SELL 100%
        
    # Policy Rule 3: Depressed Price with Safe Storage -> HOLD for recovery
    if shelf_life_used_ratio <= 0.40 and (premium_pct < -2.0 or freshness_adjusted_net < baseline_price * 0.85):
        return 0  # HOLD
        
    # Policy Rule 4: Highly Durable Grain with Minimal Storage -> HOLD
    if shelf_life_used_ratio <= 0.30 and perishability <= 4:
        return 0  # HOLD
        
    # Policy Rule 5: Solid Margin & Moderate Risk -> SELL 50% (Hedge remaining batch)
    return 1  # SELL 50%
