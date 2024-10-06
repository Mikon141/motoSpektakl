import os
from pathlib import Path
from django.conf.urls.static import static  # Dodany import

BASE_DIR = Path(__file__).resolve().parent.parent

# Ustawienia dla plików statycznych
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Ustawienia dla plików multimedialnych
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Konfiguracja logowania
LOGIN_REDIRECT_URL = '/account/'

# Sekretne klucze i ustawienia bezpieczeństwa
SECRET_KEY = 'z@y&-d$qbs!vw800y4a@7x=oe09)=!^=r3nh55(($i^7m_@nb9'
ALLOWED_HOSTS = []

# Aplikacje zainstalowane
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'widget_tweaks',
    'motoSpektakl',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'motoSpektakl.urls'

# Konfiguracja szablonów
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'motoSpektakl', 'templates')],
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

WSGI_APPLICATION = 'motoSpektakl.wsgi.application'

# Baza danych
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Walidatory haseł
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Konfiguracja SMTP dla Gmaila
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_HOST_USER = 'motospektakl@gmail.com'
EMAIL_HOST_PASSWORD = 'nkvumvoplsfhnixa'
DEFAULT_FROM_EMAIL = 'motospektakl@gmail.com'

# Ustawienia języka i strefy czasowej
LANGUAGE_CODE = 'pl'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Tryb debugowania
DEBUG = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Obsługa plików statycznych i multimedialnych podczas debugowania
if DEBUG:
    urlpatterns = static(MEDIA_URL, document_root=MEDIA_ROOT)
    urlpatterns += static(STATIC_URL, document_root=STATICFILES_DIRS[0])