from dotenv import load_dotenv
import os
from mm import KalshiTradingAPI
import logging

load_dotenv()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("debug")

api = KalshiTradingAPI(
    api_key_id=os.getenv("KALSHI_API_KEY_ID"),
    private_key_path=os.getenv("KALSHI_PRIVATE_KEY_PATH"),
    market_ticker="KXBTCD-25OCT1117-T112999.99",
    base_url=os.getenv("KALSHI_BASE_URL"),
    logger=logger,
)

# Test public endpoint (works)
print("\n=== Testing PUBLIC endpoint (markets) ===")
try:
    price = api.get_price()
    print(f"✓ Success: {price}")
except Exception as e:
    print(f"✗ Failed: {e}")

# Test private endpoint (fails)
print("\n=== Testing PRIVATE endpoint (positions) ===")
try:
    position = api.get_position()
    print(f"✓ Success: Position = {position}")
except Exception as e:
    print(f"✗ Failed: {e}")

# Check if API key might be for demo environment
print("\n=== Checking API Configuration ===")
print(f"Base URL: {os.getenv('KALSHI_BASE_URL')}")
print(f"API Key ID: {os.getenv('KALSHI_API_KEY_ID')}")