from dotenv import load_dotenv
import os
from mm import KalshiTradingAPI
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test")

print("API Key ID:", os.getenv("KALSHI_API_KEY_ID"))
print("Private Key Path:", os.getenv("KALSHI_PRIVATE_KEY_PATH"))
print("Base URL:", os.getenv("KALSHI_BASE_URL"))

try:
    api = KalshiTradingAPI(
        api_key_id=os.getenv("KALSHI_API_KEY_ID"),
        private_key_path=os.getenv("KALSHI_PRIVATE_KEY_PATH"),
        market_ticker="KXBTCD-25OCT1117-T112999.99",
        base_url=os.getenv("KALSHI_BASE_URL"),
        logger=logger,
    )
    print("API initialized successfully!")
    
    price = api.get_price()
    print(f"Got price: {price}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
