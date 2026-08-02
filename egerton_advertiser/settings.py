import os
import sys
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
import dj_database_url
import environ

# Initialize environment variables
env = environ.Env(
    DEBUG=(bool, False),
    SECRET_KEY=(str, ''),
    DATABASE_URL=(str, ''),
    ALLOWED_HOSTS=(list, []),
    REDIS_URL=(str, 'redis://localhost:6379/0'),
    EMAIL_HOST=(str, ''),
    EMAIL_PORT=(int, 587),
    EMAIL_HOST_USER=(str, ''),
    EMAIL_HOST_PASSWORD=(str, ''),
    DEFAULT_FROM_EMAIL=(str, ''),
    ADMIN_EMAIL=(str, ''),
    SITE_NAME=(str, 'The Egerton Advertiser'),
    SITE_URL=(str, 'http://localhost:8000'),
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Take environment variables from .env file
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY', default='django-insecure-^@*8h8i&y3s@3b0=z$5xq9@v*p&b!4x2r%6n0g)l^7w4!j2k%4')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG', default=False)

# ALLOWED_HOSTS - Added Render.com URL
ALLOWED_HOSTS = env('ALLOWED_HOSTS', default=[
    'localhost', 
    '127.0.0.1', 
    '.theegertonadvertiser.com',
    'egerton-advertiser.onrender.com',  # ADDED Render.com URL
    'egerton-advertiser.onrender.com',
    '.onrender.com',  # Allows all Render.com subdomains
])

# Application definition
INSTALLED_APPS = [
    # Django default apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.humanize',
    
    # Third-party apps
    'crispy_forms',
    'crispy_bootstrap5',
    'ckeditor',
    'ckeditor_uploader',
    'django_htmx',
    'django_celery_beat',
    'django_celery_results',
    'django_redis',
    'storages',
    'compressor',
    'django_filters',
    'django_extensions',
    'drf_yasg',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'django_cleanup.apps.CleanupConfig',
    'django_ratelimit',
    'django_recaptcha',
    # 'django_db_logger',  # REMOVED - was causing errors
    
    # Local apps
    'apps.accounts',
    'apps.articles',
    'apps.categories',
    'apps.tags',
    'apps.comments',
    'apps.advertisements',
    'apps.media_library',
    'apps.newsletter',
    'apps.contacts',
    'apps.analytics',
    'apps.search',
    'apps.notifications',
    'apps.dashboard',
    'apps.settings_manager',
]

# Optional development apps
if DEBUG:
    INSTALLED_APPS += [
        'debug_toolbar',
        'django_seed',
    ]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
    # 'django_db_logger.middleware.DatabaseLogMiddleware',  # REMOVED
    'apps.accounts.middleware.ActivityLogMiddleware',
    'apps.analytics.middleware.AnalyticsMiddleware',
    'apps.notifications.middleware.NotificationMiddleware',
]

ROOT_URLCONF = 'egerton_advertiser.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'apps.settings_manager.context_processors.site_settings',
                'apps.notifications.context_processors.notification_count',
                'apps.articles.context_processors.category_menu',
            ],
            'libraries': {
                'custom_filters': 'apps.articles.templatetags.custom_filters',
                'analytics_tags': 'apps.analytics.templatetags.analytics_tags',
            }
        },
    },
]

WSGI_APPLICATION = 'egerton_advertiser.wsgi.application'

# Database
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///' + str(BASE_DIR / 'db.sqlite3'),
        conn_max_age=600,
        ssl_require=False
    )
}

# Additional database configuration for production
if not DEBUG:
    DATABASES['default']['OPTIONS'] = {
        'connect_timeout': 10,
        'options': '-c statement_timeout=30000',
    }

# Multiple database support with read replicas
DATABASE_ROUTERS = ['egerton_advertiser.db_router.DatabaseRouter']

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    {
        'NAME': 'apps.accounts.validators.CustomPasswordValidator',
    },
]

# Authentication
AUTH_USER_MODEL = 'accounts.User'
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard:home'
LOGOUT_REDIRECT_URL = 'home'
LOGIN_REDIRECT_URL = 'dashboard:home'
LOGOUT_URL = 'logout'
AUTH_LOGOUT_URL = 'logout'

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
    BASE_DIR / 'apps/accounts/static',
    BASE_DIR / 'apps/articles/static',
    BASE_DIR / 'apps/dashboard/static',
]

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000

# Content Security Policy
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Security settings for production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = True
    SESSION_COOKIE_AGE = 1209600  # 2 weeks
    SESSION_SAVE_EVERY_REQUEST = True

# CORS settings - Added Render.com URL
CORS_ALLOWED_ORIGINS = env('CORS_ALLOWED_ORIGINS', default=[
    'http://localhost:3000', 
    'http://localhost:8000',
    'https://egerton-advertiser.onrender.com',  # ADDED
    'http://egerton-advertiser.onrender.com',
])
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Cache settings
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': env('REDIS_URL', default='redis://localhost:6379/0'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'RETRY_ON_TIMEOUT': True,
            'MAX_CONNECTIONS': 1000,
            'CONNECTION_POOL_CLASS': 'redis.connection.BlockingConnectionPool',
        },
        'KEY_PREFIX': 'egerton',
        'TIMEOUT': 300,
    },
    'page_cache': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': env('REDIS_URL', default='redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
        },
        'KEY_PREFIX': 'page_cache',
        'TIMEOUT': 900,
    },
    'session_cache': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': env('REDIS_URL', default='redis://localhost:6379/2'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
        },
        'KEY_PREFIX': 'session_cache',
        'TIMEOUT': 86400,
    },
}

# Session settings
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'session_cache'

# Email settings
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = env('EMAIL_HOST', default='')
    EMAIL_PORT = env('EMAIL_PORT', default=587)
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
    EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
    DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='noreply@theegertonadvertiser.com')
    EMAIL_USE_SSL = False
    EMAIL_TIMEOUT = 30

# Admin email
ADMINS = [('Admin', env('ADMIN_EMAIL', default='admin@theegertonadvertiser.com'))]
MANAGERS = ADMINS

# Celery settings
CELERY_BROKER_URL = env('REDIS_URL', default='redis://localhost:6379/3')
CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'default'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_WORKER_CONCURRENCY = 4
CELERY_MAX_TASKS_PER_CHILD = 50

# Celery beat schedule
CELERY_BEAT_SCHEDULE = {
    'send-newsletter-daily': {
        'task': 'apps.newsletter.tasks.send_daily_newsletter',
        'schedule': 86400,  # 24 hours
    },
    'send-newsletter-weekly': {
        'task': 'apps.newsletter.tasks.send_weekly_newsletter',
        'schedule': 604800,  # 7 days
    },
    'cleanup-expired-ads': {
        'task': 'apps.advertisements.tasks.cleanup_expired_ads',
        'schedule': 3600,  # 1 hour
    },
    'update-analytics': {
        'task': 'apps.analytics.tasks.update_analytics',
        'schedule': 3600,  # 1 hour
    },
    'send-email-digest': {
        'task': 'apps.notifications.tasks.send_email_digest',
        'schedule': 86400,  # 24 hours
    },
}

# Django debug toolbar
if DEBUG:
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
        'INTERCEPT_REDIRECTS': False,
        'SHOW_TEMPLATE_CONTEXT': True,
    }
    DEBUG_TOOLBAR_PANELS = [
        'debug_toolbar.panels.history.HistoryPanel',
        'debug_toolbar.panels.versions.VersionsPanel',
        'debug_toolbar.panels.timer.TimerPanel',
        'debug_toolbar.panels.settings.SettingsPanel',
        'debug_toolbar.panels.headers.HeadersPanel',
        'debug_toolbar.panels.request.RequestPanel',
        'debug_toolbar.panels.sql.SQLPanel',
        'debug_toolbar.panels.staticfiles.StaticFilesPanel',
        'debug_toolbar.panels.templates.TemplatesPanel',
        'debug_toolbar.panels.cache.CachePanel',
        'debug_toolbar.panels.signals.SignalsPanel',
        'debug_toolbar.panels.logging.LoggingPanel',
        'debug_toolbar.panels.redirects.RedirectsPanel',
        'debug_toolbar.panels.profiling.ProfilingPanel',
    ]

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day',
    },
}

# Rate limiting
RATELIMIT_ENABLE = True
RATELIMIT_VIEW = 'apps.accounts.views.rate_limit_exceeded'
RATELIMIT_USE_CACHE = 'default'

# Google reCAPTCHA
RECAPTCHA_PUBLIC_KEY = env('RECAPTCHA_PUBLIC_KEY', default='')
RECAPTCHA_PRIVATE_KEY = env('RECAPTCHA_PRIVATE_KEY', default='')
RECAPTCHA_REQUIRED_SCORE = 0.85

# CKEditor settings
CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_IMAGE_BACKEND = 'pillow'
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 500,
        'width': '100%',
        'extraPlugins': ','.join([
            'uploadimage',
            'uploadfile',
            'image2',
            'codesnippet',
            'widget',
            'lineutils',
            'autolink',
            'autoembed',
        ]),
        'toolbar_Full': [
            ['Format', 'Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', 'RemoveFormat'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', 'CreateDiv', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['Link', 'Unlink', 'Anchor'],
            ['Image', 'Table', 'HorizontalRule', 'SpecialChar', 'PageBreak'],
            ['CodeSnippet', 'Source'],
            ['Maximize', 'ShowBlocks'],
        ],
        'toolbar_Styled': [
            ['Format', 'Bold', 'Italic', 'Underline', 'Strike'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent'],
            ['Link', 'Unlink'],
            ['Image', 'Table'],
            ['CodeSnippet', 'Source'],
        ],
        'removePlugins': 'stylesheetparser',
        'filebrowserUploadUrl': '/media/ckeditor/upload/',
        'filebrowserBrowseUrl': '/media/ckeditor/browse/',
        'filebrowserImageUploadUrl': '/media/ckeditor/upload/',
        'filebrowserImageBrowseUrl': '/media/ckeditor/browse/',
        'language': 'en',
        'allowedContent': True,
        'autoGrow_minHeight': 200,
        'autoGrow_maxHeight': 800,
        'resize_enabled': True,
        'pasteFromWordPromptCleanup': True,
        'pasteFromWordRemoveFontStyles': True,
        'pasteFromWordRemoveStyles': True,
        'basicEntities': True,
        'entities': True,
        'entities_greek': True,
        'entities_latin': False,
    },
    'basic': {
        'toolbar': 'Basic',
        'height': 200,
        'width': '100%',
        'toolbar_Basic': [
            ['Bold', 'Italic', 'Underline'],
            ['NumberedList', 'BulletedList'],
            ['Link', 'Unlink'],
            ['Image'],
        ],
        'removePlugins': 'stylesheetparser',
        'filebrowserUploadUrl': '/media/ckeditor/upload/',
        'filebrowserBrowseUrl': '/media/ckeditor/browse/',
    },
}

# Media library settings
MEDIA_ALLOWED_EXTENSIONS = {
    'image': ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp', '.ico'],
    'video': ['.mp4', '.webm', '.ogg', '.mov', '.avi', '.mkv'],
    'audio': ['.mp3', '.wav', '.ogg', '.m4a', '.flac'],
    'document': ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.rtf'],
}
MEDIA_MAX_FILE_SIZE = 10485760  # 10MB
MEDIA_MAX_IMAGE_SIZE = 4096  # 4096x4096 pixels

# Newsletter settings
NEWSLETTER_DEFAULT_FREQUENCY = 'weekly'
NEWSLETTER_MAX_ATTEMPTS = 3
NEWSLETTER_SEND_INTERVAL = 60  # seconds between emails

# Advertisement settings
AD_DEFAULT_PRIORITY = 10
AD_MAX_PRIORITY = 100
AD_CLICK_TRACKING_ENABLED = True
AD_VIEW_TRACKING_ENABLED = True

# Analytics settings
ANALYTICS_ENABLED = True
ANALYTICS_SAMPLE_RATE = 1.0
ANALYTICS_REAL_TIME_ENABLED = True
ANALYTICS_RETAIN_DAYS = 365

# Search settings
SEARCH_MIN_QUERY_LENGTH = 2
SEARCH_MAX_RESULTS = 1000
SEARCH_TRACK_QUERIES = True

# Notification settings
NOTIFICATION_BATCH_SIZE = 100
NOTIFICATION_PUSH_ENABLED = True
NOTIFICATION_SMS_ENABLED = False

# Site settings
SITE_ID = 1
SITE_NAME = env('SITE_NAME', default='The Egerton Advertiser')
SITE_URL = env('SITE_URL', default='http://localhost:8000')

# Session settings
SESSION_COOKIE_NAME = 'egerton_sessionid'
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_DOMAIN = '.theegertonadvertiser.com' if not DEBUG else None

# CSRF settings - Added Render.com URL
CSRF_COOKIE_NAME = 'egerton_csrftoken'
CSRF_HEADER_NAME = 'HTTP_X_CSRFTOKEN'
CSRF_TRUSTED_ORIGINS = [
    'https://*.theegertonadvertiser.com',
    'https://*.egertonadvertiser.com',
    'https://egerton-advertiser.onrender.com',  # ADDED
    'http://egerton-advertiser.onrender.com',
]

# Logging configuration - REMOVED 'db' handler
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'filters': ['require_debug_true'],
        },
        'file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs/django.log',
            'maxBytes': 10485760,
            'backupCount': 10,
            'formatter': 'verbose',
            'filters': ['require_debug_false'],
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
        },
        'security': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs/security.log',
            'maxBytes': 10485760,
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file', 'mail_admins'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console', 'file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.security': {
            'handlers': ['security', 'mail_admins'],
            'level': 'WARNING',
            'propagate': True,
        },
        'apps': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': True,
        },
        'apps.accounts': {
            'handlers': ['console', 'security'],
            'level': 'INFO',
            'propagate': True,
        },
        'apps.analytics': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'celery': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Django Cleanup
DJANGO_CLEANUP = {
    'auto_cleanup': True,
    'cleanup_after_commit': True,
}

# Compressor settings
COMPRESS_ENABLED = not DEBUG
COMPRESS_OFFLINE = not DEBUG
COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.rCSSMinFilter',
]
COMPRESS_JS_FILTERS = [
    'compressor.filters.jsmin.JSMinFilter',
]
COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_libsass.SassCompiler'),
)
COMPRESS_CACHE_BACKEND = 'page_cache'
COMPRESS_STORAGE = 'compressor.storage.CompressorFileStorage'

# AWS S3 Storage (for production)
if not DEBUG:
    AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID', default='')
    AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY', default='')
    AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME', default='')
    AWS_S3_CUSTOM_DOMAIN = env('AWS_S3_CUSTOM_DOMAIN', default='')
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }
    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL = 'public-read'
    AWS_QUERYSTRING_AUTH = False
    AWS_S3_REGION_NAME = 'us-east-1'
    AWS_S3_SIGNATURE_VERSION = 's3v4'
    
    if AWS_STORAGE_BUCKET_NAME:
        DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
        STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
        AWS_LOCATION = 'media'
        STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
        MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'

# Celery beat scheduler
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# Django extensions
SHELL_PLUS = 'ipython'
SHELL_PLUS_PRINT_SQL = False

# Swagger/OpenAPI settings
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
    'USE_SESSION_AUTH': True,
    'JSON_EDITOR': True,
    'DEFAULT_MODEL_RENDERER': 'drf_yasg.renderers.SwaggerUIRenderer',
}

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom settings
NEWSPAPER_SETTINGS = {
    'ARTICLES_PER_PAGE': 20,
    'COMMENTS_PER_PAGE': 25,
    'MAX_UPLOAD_SIZE': 5242880,
    'ALLOWED_IMAGE_TYPES': ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
    'BREAKING_NEWS_LIMIT': 5,
    'FEATURED_ARTICLES_LIMIT': 6,
    'RELATED_ARTICLES_LIMIT': 5,
    'POPULAR_ARTICLES_LIMIT': 10,
    'RECENT_COMMENTS_LIMIT': 10,
    'ACTIVITY_LOG_DAYS': 30,
    'CACHE_TIMEOUT': 300,
    'SEARCH_RESULTS_PER_PAGE': 20,
    'DASHBOARD_WIDGETS_COLUMNS': 4,
}

# Database router
DATABASE_ROUTERS = []

# Custom user model
AUTH_USER_MODEL = 'accounts.User'

# Create necessary directories
for directory in ['logs', 'media', 'static']:
    path = BASE_DIR / directory
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

# Production specific settings
if not DEBUG:
    # Security headers
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # Trusted origins - Added Render.com
    CSRF_TRUSTED_ORIGINS = [
        'https://*.theegertonadvertiser.com',
        'https://egerton-advertiser.onrender.com'
    ]
    
    # Security middleware
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# ============================================
# WEATHER API SETTINGS
# ============================================
OPENWEATHER_API_KEY = env('OPENWEATHER_API_KEY', default='43d50a5567a266018562b68f961eaecc')
OPENWEATHER_BASE_URL = 'https://api.openweathermap.org/data/2.5/'

# Print settings for debugging
if DEBUG:
    print(f"\n{'='*50}")
    print(f"DJANGO SETTINGS LOADED")
    print(f"DEBUG: {DEBUG}")
    print(f"DATABASE: {DATABASES['default']['ENGINE']}")
    print(f"MEDIA_ROOT: {MEDIA_ROOT}")
    print(f"STATIC_ROOT: {STATIC_ROOT}")
    print(f"{'='*50}\n")