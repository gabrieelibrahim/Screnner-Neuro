from typing import List, Dict, Any
import pandas as pd

class RankingEngine:
    @staticmethod
    def score_signal(row: pd.Series) -> float:
        """
        Calculate weighted score for a stock based on its indicators.
        Higher score is better.
        """
        score = 0.0
        
        # 1. RVOL Score (Weight: 40%)
        # Cap RVOL at 10 to prevent extreme outliers skewing the rank
        rvol = min(row['RVOL'], 10.0) if pd.notna(row['RVOL']) else 0
        score += rvol * 10  # Max 100 points
        
        # 2. Trend Quality (Weight: 20%)
        # Distance between EMA20 and EMA50 (wider is stronger trend)
        ema20 = row['EMA_20']
        ema50 = row['EMA_50']
        if pd.notna(ema20) and pd.notna(ema50) and ema50 > 0:
            trend_dist = (ema20 - ema50) / ema50 * 100
            score += min(trend_dist * 2, 50) # Cap at 50 points
            
        # 3. RSI Quality (Weight: 20%)
        # Ideal RSI is around 65. Too high (80+) is overbought, too low (<55) lacks momentum.
        rsi = row['RSI_14']
        if pd.notna(rsi):
            if 60 <= rsi <= 70:
                score += 40
            elif 55 <= rsi < 60 or 70 < rsi <= 75:
                score += 20
                
        # 4. Candle Quality (Weight: 20%)
        # Solid bullish candle (Open near Low, Close near High)
        c_open, c_high, c_low, c_close = row['Open'], row['High'], row['Low'], row['Close']
        if (c_high - c_low) > 0:
            body_size = (c_close - c_open) / (c_high - c_low)
            if body_size > 0:
                score += body_size * 40 # Max 40 points for full marubozu
                
        return round(score, 2)

    @classmethod
    def rank_candidates(cls, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sort candidates based on their calculated score in descending order.
        candidates list format: [{"ticker": "ADRO.JK", "row": <pd.Series>, "metadata": {...}}, ...]
        """
        for candidate in candidates:
            candidate['score'] = cls.score_signal(candidate['row'])
            
        # Sort by score descending
        ranked = sorted(candidates, key=lambda x: x['score'], reverse=True)
        return ranked
