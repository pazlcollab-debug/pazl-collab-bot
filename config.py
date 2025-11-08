import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
ADMIN_ID = int(os.getenv('ADMIN_ID', 0))
DEFAULT_PHOTO_URL = os.getenv('DEFAULT_PHOTO_URL', 'https://example.com/default.png')
