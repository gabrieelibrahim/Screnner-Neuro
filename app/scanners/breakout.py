import pandas as pd
from typing import Optional, Dict, Any
from app.core.config import settings

class BreakoutScanner:
    @staticmethod
    def is_breakout(row: pd.Series, prev_row: pd.Series) -> tuple[bool, str, Dict[str, Any]]:
        """
        Check if the current candle represents a valid, high-quality breakout.
        Returns: (is_valid, reason_if_invalid, metadata)
        """
        try:
            close = row['Close']
            open_price = row['Open']
            high = row['High']
            low = row['Low']
            rvol = row['RVOL']
            rsi = row['RSI_14']
            ema20 = row['EMA_20']
            ema50 = row['EMA_50']
            resistance = row['Resistance_20']
            volume = row['Volume']
            
            metadata = {
                "close": float(close),
                "rvol": float(rvol) if pd.notna(rvol) else 0.0,
                "rsi": float(rsi) if pd.notna(rsi) else 0.0,
                "resistance": float(resistance) if pd.notna(resistance) else 0.0,
            }

            # 1. PRIMARY CONDITIONS
            if pd.isna(resistance) or close <= resistance:
                return False, "Not breaking resistance", metadata
                
            if rvol < settings.RVOL_THRESHOLD:
                return False, f"Low RVOL ({rvol:.1f} < {settings.RVOL_THRESHOLD})", metadata
                
            if close <= ema20:
                return False, "Price below EMA20", metadata
                
            if ema20 <= ema50:
                return False, "EMA20 below EMA50 (No Trend)", metadata
                
            if not (55 <= rsi <= 75):
                return False, f"RSI out of healthy range ({rsi:.1f})", metadata
                
            if volume < settings.MIN_VOLUME:
                return False, "Volume below minimum threshold", metadata

            # 2. ANTI FAKEOUT FILTER
            # Avoid rejection candle (long upper wick). Close should be in upper 50% of candle.
            candle_range = high - low
            if candle_range == 0:
                return False, "Zero candle range", metadata
                
            close_position = (close - low) / candle_range
            if close_position < 0.5:
                return False, f"Rejection candle (Close at {close_position*100:.1f}%)", metadata
                
            # Avoid over-extended breakouts (price way too far from EMA20)
            # If price is > 15% above EMA20, it's risky (chasing)
            if (close - ema20) / ema20 > 0.15:
                return False, "Overextended from EMA20", metadata

            return True, "Valid Breakout", metadata
            
        except Exception as e:
            return False, f"Error calculating: {str(e)}", {}
