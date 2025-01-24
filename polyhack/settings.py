import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'your-secret-key'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Ngrok configuration
NGROK_URL = 'https://b43e-41-230-221-34.ngrok-free.app'
NGROK_HOST = 'b43e-41-230-221-34.ngrok-free.app'

# ALLOWED_HOSTS configuration
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '192.168.146.1',
    NGROK_HOST,  # Add the ngrok host
    'b43e-41-230-221-34.ngrok-free.app',  # Explicit ngrok domain
    '.ngrok-free.app',  # Allow all ngrok subdomains
]

# CSRF settings
CSRF_TRUSTED_ORIGINS = [
    NGROK_URL,
    'https://*.ngrok-free.app',
]

# Print debug info
print("Django settings loaded with:")
print(f"ALLOWED_HOSTS: {ALLOWED_HOSTS}")

# FFmpeg configuration
FFMPEG_BIN = r"C:\ffmpeg\bin\ffmpeg.exe"  # Full path to ffmpeg executable

# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Create necessary directories
MEDIA_DIRS = [
    os.path.join(MEDIA_ROOT, 'lessons', 'videos'),
    os.path.join(MEDIA_ROOT, 'lessons', 'pdfs'),
    os.path.join(MEDIA_ROOT, 'temp'),
]

for dir_path in MEDIA_DIRS:
    os.makedirs(dir_path, exist_ok=True)

# Static files configuration
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUDIO_ROOT = os.path.join(BASE_DIR, 'static', 'audio')

# Template configuration
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
] 

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'user',
    'teachers',
    'students',
    'classes',
    'lessons',
    'django_ngrok',
    'bot'
] 

# For debugging
print("Settings loaded with:")
print(f"ALLOWED_HOSTS: {ALLOWED_HOSTS}") 

os.makedirs(AUDIO_ROOT, exist_ok=True)

from dotenv import load_dotenv
load_dotenv()

# Then get the API key like this
API_KEY = os.getenv('OPENAI_API_KEY')