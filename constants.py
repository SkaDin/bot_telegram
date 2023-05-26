import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


BASE_DIR = Path(__file__).parent
DT_FORMAT = '%d.%m.%Y %H:%M:%S'
CONVERTER_PRESSURE = 0.750064
KEY = os.getenv('KEY')
LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
TOKEN = os.getenv('TOKEN')
URL_CAT = 'https://api.thecatapi.com/v1/images/search'
URL_TRANSLATE = 'https://microsoft-translator-text.p.rapidapi.com/translate'
URL_WEATHER = "https://ai-weather-by-meteosource.p.rapidapi.com/current"
