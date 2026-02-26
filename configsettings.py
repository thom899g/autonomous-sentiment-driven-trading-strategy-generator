"""
Configuration management for the sentiment-driven trading system.
Uses environment variables with sensible defaults for all critical parameters.
"""
import os
from dataclasses import dataclass
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()

@dataclass
class FirebaseConfig:
    """Firebase configuration with validation"""
    project_id: str
    private_key_id: str
    private_key: str
    client_email: str
    
    def __post_init__(self):
        """Validate Firebase configuration"""
        if not self.project_id:
            raise ValueError("Firebase project_id is required")
        if not all([self.private_key_id, self.private_key, self.client_email]):
            raise ValueError("Incomplete Firebase credentials")

@dataclass
class TradingConfig:
    """Trading system configuration"""
    # Exchange settings
    exchange_id: str = "binance"
    symbol: str = "BTC/USDT"
    timeframe: str = "1h"
    
    # Risk management
    max_position_size: float = 0.1  # 10% of portfolio
    stop_loss_pct: float = 0.02     # 2% stop loss
    take_profit_pct: float = 0.05   # 5% take profit
    
    # Trading hours (UTC)
    trading_start_hour: int = 0
    trading_end_hour: int = 23
    
    def validate(self):
        """Validate trading configuration"""
        if self.max_position_size <= 0 or self.max_position_size > 1:
            raise ValueError("max_position_size must be between 0 and 1")
        if self.stop_loss_pct <= 0:
            raise ValueError("stop_loss_pct must be positive")
        if self.take_profit_pct <= 0:
            raise ValueError("take_profit_pct must be positive")

@dataclass
class SentimentConfig:
    """Sentiment analysis configuration"""
    sources: List[str] = None
    update_interval_minutes: int = 5
    sentiment_threshold: float = 0.3
    min_confidence: float = 0.7
    
    def __post_init__(self):
        if self.sources is None:
            self.sources = ["twitter", "reddit", "news"]
        if self.sentiment_threshold < -1 or self.sentiment_threshold > 1:
            raise ValueError("sentiment_threshold must be between -1 and 1")

class ConfigManager:
    """Central configuration manager with validation"""
    
    def __init__(self):
        self.firebase = self._load_firebase_config()
        self.trading = self._load_trading_config()
        self.sentiment = self._load_sentiment_config()
        self._validate_all()
    
    def _load_firebase_config(self) -> FirebaseConfig:
        """Load Firebase configuration from environment"""
        try:
            return FirebaseConfig(
                project_id=os.getenv("FIREBASE_PROJECT_ID", ""),
                private_key_id=os.getenv("FIREBASE_PRIVATE_KEY_ID", ""),
                private_key=os.getenv("FIREBASE_PRIVATE_KEY", "").replace('\\n', '\n'),
                client_email=os.getenv("FIREBASE_CLIENT_EMAIL", "")
            )
        except Exception as e:
            raise ValueError(f"Failed to load Firebase config: {e}")
    
    def _load_trading_config(self) -> TradingConfig:
        """Load trading configuration"""
        config = TradingConfig(
            exchange_id=os.getenv("EXCHANGE_ID", "binance"),
            symbol=os.getenv("TRADING_SYMBOL", "BTC/USDT"),
            timeframe=os.getenv("TIMEFRAME", "1h"),
            max_position_size=float(os.getenv("MAX_POSITION_SIZE", "0.1")),
            stop_loss_pct=float(os.getenv("STOP_LOSS_PCT", "0.02")),
            take_profit_pct=float(os.getenv("TAKE_PROFIT_PCT", "0.05"))
        )
        config.validate()
        return config
    
    def _load_sentiment_config(self) -> SentimentConfig:
        """Load sentiment configuration"""
        sources_str = os.getenv("SENTIMENT_SOURCES", "twitter,reddit,news")
        return SentimentConfig(
            sources=[s.strip() for s in sources_str.split(",")],
            update_interval_minutes=int(os.getenv("SENTIMENT_UPDATE_MINUTES", "5")),
            sentiment_threshold=float(os.getenv("SENTIMENT_THRESHOLD", "0.3")),
            min_confidence=float(os.getenv("MIN_CONFIDENCE", "0.7"))
        )
    
    def _validate_all(self):
        """Validate all configurations"""
        self.trading.validate()
        self.sentiment.__post_init__()
        
        # Check for required environment variables
        required_vars = ["FIREBASE_PROJECT_ID", "FIREBASE_PRIVATE_KEY_ID"]
        missing = [var for var in required_vars if not os.getenv(var)]
        if missing:
            raise ValueError(f"Missing required environment variables: {missing}")

# Global configuration instance
config = ConfigManager()