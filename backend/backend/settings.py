from pathlib import Path

# ====================================================================
# PATHS
# ====================================================================
BASE_DIR = Path(__file__).resolve().parent.parent

# ====================================================================
# BASIC SETTINGS
# ====================================================================
SECRET_KEY = 'dev-key-change-me'   # Change for production
DEBUG = True

# Allow everything in dev mode
ALLOWED_HOSTS = ['*']

# ====================================================================
# INSTALLED APPS
# ====================================================================
INSTALLED_APPS = [
    # Django core apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',

    # Local apps
    'api',
]

# ====================================================================
# MIDDLEWARE
# ====================================================================
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # must be at the top!
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

# ====================================================================
# URLS / WSGI
# ====================================================================
ROOT_URLCONF = 'backend.urls'
WSGI_APPLICATION = 'backend.wsgi.application'

# ====================================================================
# TEMPLATES
# ====================================================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # no templates needed for API-only backend
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

# ====================================================================
# DATABASE
# ====================================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ====================================================================
# MEDIA / STATIC
# ====================================================================
STATIC_URL = '/static/'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'   # backend/media/

# ====================================================================
# REST FRAMEWORK CONFIG
# ====================================================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}

# ====================================================================
# UPLOAD LIMITS
# ====================================================================
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5 MB

# ====================================================================
# CORS CONFIG (DEV: allow React frontend to call API)
# ====================================================================
# Allow EVERYTHING in dev mode for simplicity
CORS_ALLOW_ALL_ORIGINS = True

# If you disable ALLOW_ALL, this list will be used
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]

# ====================================================================
# INTERNATIONALIZATION
