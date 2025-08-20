from os import getenv
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(".env.test"))

SECRET_PAYMENT_KEY = getenv("SECRET_PAYMENT_KEY", "")
