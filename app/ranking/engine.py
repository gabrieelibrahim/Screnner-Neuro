from typing import List, Dict, Any
import pandas as pd

class RankingEngine:
    @staticmethod
    def score_signal(row: pd.Series) -> float:
        """
        Calculate weighted score for a stock based on its indicators.
        Higher score is better.
        """
        if meta is None:
            meta = {}
            
        score = 0.0
        
        # Weights
        weights = {
            "rvol": 0.35,
            "resistance_vol": 0.25,
            "candle": 0.15,
            "trend": 0.15,
            "rsi": 0.10
        }
        
        # 1. RVOL Score
        rvol = min(row.get('RVOL', 0), 10.0) if pd.notna(row.get('RVOL')) else 0
        rvol_score = min((rvol / 5.0) * 100, 100)
        score += rvol_score * weights["rvol"]
        
        # 2. Resistance Volume Score
        res_vol = meta.get('breakout_volume_score', rvol)
        res_vol_score = min((res_vol / 4.0) * 100, 100)
        score += res_vol_score * weights["resistance_vol"]
        
        # 3. Candle Quality
        close_pos = meta.get('candle_close_pos', 0.5)
        body = meta.get('candle_body', 0.5)
        candle_score = min(((close_pos * 0.7) + (body * 0.3)) * 100, 100)
        score += candle_score * weights["candle"]
        
        # 4. Trend Quality
        ema20 = row.get('EMA_20', 0)
        ema50 = row.get('EMA_50', 0)
        if pd.notna(ema20) and pd.notna(ema50) and ema50 > 0:
            trend_dist = min((ema20 - ema50) / ema50 * 100, 100)
            score += max(trend_dist, 0) * weights["trend"]
            
        # 5. RSI Quality
        rsi = row.get('RSI_14', 50)
        if pd.notna(rsi):
            if 60 <= rsi <= 70:
                rsi_score = 100
            elif 55 <= rsi < 60 or 70 < rsi <= 75:
                rsi_score = 50
            else:
                rsi_score = 0
            score += rsi_score * weights["rsi"]
                
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
