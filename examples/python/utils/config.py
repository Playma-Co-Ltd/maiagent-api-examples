import os
from pathlib import Path
from dotenv import load_dotenv

# Try to load .env file if it exists
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# API Configuration
API_KEY = os.getenv('MAIAGENT_API_KEY', '<Please set your API key>')
BASE_URL = os.getenv('MAIAGENT_BASE_URL', '<Please set your base url>')

# Chatbot Configuration
CHATBOT_ID = os.getenv('MAIAGENT_CHATBOT_ID', '<Please set your chatbot id>')

# Web Chat Configuration
WEB_CHAT_ID = os.getenv('MAIAGENT_WEB_CHAT_ID', '<Please set your webchat id>')

# Storage Configuration
