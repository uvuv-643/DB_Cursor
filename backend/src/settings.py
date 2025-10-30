import os

from dotenv import load_dotenv


load_dotenv()

# Redis
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "your_password")

# Encryption
SECRET_KEY = os.getenv("SECRET_KEY")
EXPIRE_MINUTES = int(os.getenv("EXPIRE_MINUTES"))

# Yandex Cloud
YANDEX_CLOUD_API_KEY = os.getenv("YANDEX_CLOUD_API_KEY")
YANDEX_CLOUD_FOLDER = os.getenv("YANDEX_CLOUD_FOLDER")
YANDEX_CLOUD_MODEL = os.getenv("YANDEX_CLOUD_MODEL")
