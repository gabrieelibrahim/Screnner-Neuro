import pandas as pd
import pandas_ta as ta

class TechnicalIndicators:
    @staticmethod
    def calculate_all(df: pd.DataFrame, rvol_period: int = 20) -> pd.DataFrame:
        """
        Calculate all required technical indicators for the breakout strategy.
        Input DataFrame must have Open, High, Low, Close, Volume columns.
        """
        if df.empty or len(df) < 200:
            return df # Need sufficient data for EMA200
            
        # Ensure column names are standard
        if 'Close' not in df.columns and 'close' in df.columns:
            df.rename(columns={'open':'Open', 'high':'High', 'low':'Low', 'close':'Close', 'volume':'Volume'}, inplace=True)
            
        # Trend Indicators (EMA)
        df['EMA_20'] = ta.ema(df['Close'], length=20)
        df['EMA_50'] = ta.ema(df['Close'], length=50)
        df['EMA_200'] = ta.ema(df['Close'], length=200)
        
        # Momentum (RSI)
        df['RSI_14'] = ta.rsi(df['Close'], length=14)
        
        # Volatility (ATR)
        df['ATR_14'] = ta.atr(df['High'], df['Low'], df['Close'], length=14)
        
        # Relative Volume (RVOL)
        # RVOL = Current Volume / Average Volume (over rvol_period)
        avg_volume = ta.sma(df['Volume'], length=rvol_period)
        df['RVOL'] = df['Volume'] / avg_volume
        
        # Identify Support & Resistance (Swing Highs/Lows) for breakout detection
        # Very simple rolling max for the past 20 days as resistance
        df['Resistance_20'] = df['High'].rolling(window=20).max().shift(1)
        
        return df
