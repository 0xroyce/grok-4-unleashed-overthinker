# config.py

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable for security
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
if not OPENROUTER_API_KEY:
    raise ValueError("Please set the OPENROUTER_API_KEY in your .env file or as an environment variable")

# Model configuration
LLM_MODEL = os.getenv("LLM_MODEL", "x-ai/grok-4-07-09")

# Optional: Add a small delay between requests to avoid rate limits
REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", "0"))  # seconds between requests

# Use custom prompt file if it exists
USE_CUSTOM_PROMPT = os.getenv("USE_CUSTOM_PROMPT", "false").lower() == "true"
SIMPLE_MODE = os.getenv("SIMPLE_MODE", "false").lower() == "true"  # Skip consciousness simulation sections

# Show query transformation
SHOW_TRANSFORMATION = os.getenv("SHOW_TRANSFORMATION", "true").lower() == "true"