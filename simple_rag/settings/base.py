# Copyright (C) 2021 Ibrahem Mouhamad
#
# SPDX-License-Identifier: MIT

'''
Django settings for simple_rag project.
'''

import os
import sys
import tempfile
from pathlib import Path
from corsheaders.defaults import default_headers

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = str(Path(__file__).parents[2])

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

def generate_secret_key():
    """
    Creates secret_key.py in such a way that multiple processes calling
    this will all end up with the same key (assuming that they share the
    same "keys" directory).
    """

    from django.utils.crypto import get_random_string
    keys_dir = os.path.join(BASE_DIR, 'keys')
    if not os.path.isdir(keys_dir):
        os.mkdir(keys_dir)

    secret_key_fname = 'secret_key.py' # nosec

    with tempfile.NamedTemporaryFile(
        mode='wt', dir=keys_dir, prefix=secret_key_fname + ".",
    ) as f:
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        f.write("SECRET_KEY = '{}'\n".format(get_random_string(50, chars)))

        # Make sure the file contents are written before we link to it
        # from the final location.
        f.flush()

        try:
            os.link(f.name, os.path.join(keys_dir, secret_key_fname))
        except FileExistsError:
            # Somebody else created the secret key first.
            # Discard ours and use theirs.
            pass

try:
    sys.path.append(BASE_DIR)
    from keys.secret_key import SECRET_KEY # pylint: disable=unused-import
except ModuleNotFoundError:
    generate_secret_key()
    from keys.secret_key import SECRET_KEY

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'compressor',
    'rest_framework',
    'drf_spectacular',
    'django.contrib.sites',
    'corsheaders',
    'simple_rag.apps.core',
]

SITE_ID = 1

REST_FRAMEWORK = {
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'simple_rag.apps.core.renderers.SimpleRagAPIRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
    ],
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.AcceptHeaderVersioning',
    'ALLOWED_VERSIONS': ('1.0'),
    'DEFAULT_VERSION': '1.0',
    'VERSION_PARAM': 'version',
    # Disable default handling of the 'format' query parameter by REST framework
    'URL_FORMAT_OVERRIDE': 'scheme',
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/minute',
    },
    'DEFAULT_METADATA_CLASS': 'rest_framework.metadata.SimpleMetadata',
    'DEFAULT_SCHEMA_CLASS': 'simple_rag.apps.core.schema.CustomAutoSchema',
}


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

UI_URL = ''

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
]

ROOT_URLCONF = 'simple_rag.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

ASGI_APPLICATION  = 'simple_rag.asgi.application'

# JavaScript and CSS compression
# https://django-compressor.readthedocs.io

COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.rCSSMinFilter',
]
# No compression for js files (template literals were compressed bad)
COMPRESS_JS_FILTERS = []

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = os.getenv('TZ', 'Etc/UTC')

USE_I18N = True

USE_L10N = True

USE_TZ = True

CSRF_COOKIE_NAME = 'csrftoken'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/statics/'
STATIC_ROOT = os.path.join(BASE_DIR, 'statics')
os.makedirs(STATIC_ROOT, exist_ok=True)

# Make sure to update other config files when updating these directories
DATA_ROOT = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_ROOT, exist_ok=True)

DATASETS_ROOT = os.path.join(DATA_ROOT, 'datasets')
os.makedirs(DATASETS_ROOT, exist_ok=True)

CACHE_ROOT = os.path.join(DATA_ROOT, 'cache')
os.makedirs(CACHE_ROOT, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {'format': '[%(asctime)s] %(levelname)s %(name)s: %(message)s'},
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'filters': [],
            'formatter': 'standard',
        },
        'server_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'filename': os.path.join(BASE_DIR, 'logs', 'simple_rag_server.log'),
            'formatter': 'standard',
            'maxBytes': 1024 * 1024 * 50,  # 50 MB
            'backupCount': 5,
        },
    },
    'loggers': {
        'simple_rag_server.server': {
            'handlers': ['console', 'server_file'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
        },
        'django': {
            'handlers': ['console', 'server_file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

DATA_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024  # 100 MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = None  # this django check disabled
LOCAL_LOAD_MAX_FILES_COUNT = 500
LOCAL_LOAD_MAX_FILES_SIZE = 512 * 1024 * 1024  # 512 MB


# # http://www.grantjenks.com/docs/diskcache/tutorial.html#djangocache
CACHES = {
    'default': {
        'BACKEND': 'diskcache.DjangoCache',
        'LOCATION': CACHE_ROOT,
        'TIMEOUT': None,
        'OPTIONS': {
            'size_limit': 2**40,  # 1 Tb
        },
    }
}

USE_CACHE = True

SPECTACULAR_SETTINGS = {
    'TITLE': 'Simple RAG REST API',
    'DESCRIPTION': 'REST API for Simple RAG project',
    # Statically set schema version. May also be an empty string. When used together with
    # view versioning, will become '0.0.0 (v2)' for 'v2' versioned requests.
    # Set VERSION to None if only the request version should be rendered.
    'VERSION': '1.0.0',
    'CONTACT': {
        'name': 'Ibrahem Mouhamad',
        'url': 'https://github.com/ibraym/simple-rag',
        'email': 'ibrahem.y.mouhamad@gmail.com',
    },
    'LICENSE': {
        'name': 'MIT License',
        'url': 'https://en.wikipedia.org/wiki/MIT_License',
    },
    'SERVE_PUBLIC': True,
    # 'SERVE_PERMISSIONS': ['rest_framework.permissions.IsAuthenticated'],
    # https://swagger.io/docs/open-source-tools/swagger-ui/usage/configuration/
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'displayOperationId': True,
        'displayRequestDuration': True,
        'filter': True,
        'showExtensions': True,
    },
    'TOS': 'https://www.google.com/policies/terms/',
    # OTHER SETTINGS
    # https://drf-spectacular.readthedocs.io/en/latest/settings.html
    # TODO: Our current implementation does not suppose this.
    # Need to reconsider this later. It happens, for example,
    # in TaskSerializer for data-originated fields - they can be empty.
    # https://github.com/tfranzel/drf-spectacular/issues/54
    'COMPONENT_NO_READ_ONLY_REQUIRED': True,
    # Required for correct file upload type (bytes)
    'COMPONENT_SPLIT_REQUEST': True,
    # Coercion of {pk} to {id} is controlled by SCHEMA_COERCE_PATH_PK. Additionally,
    # some libraries (e.g. drf-nested-routers) use '_pk' suffixed path variables.
    # This setting globally coerces path variables like '{user_pk}' to '{user_id}'.
    'SCHEMA_COERCE_PATH_PK_SUFFIX': True,
    'SCHEMA_PATH_PREFIX': '/api',
    'SCHEMA_PATH_PREFIX_TRIM': False,
}

# vector database server configuration
QDRANT_GATEWAY = {
    'HOST': os.getenv('QDRANT_HOST', 'qdrant'),
    'PORT': os.getenv('QDRANT_PORT', 6333),
}

# RAG settings
RAG_SETTINGS = {
    'EMBED_MODEL': None,
    'LLM': None,
    'DATASET_EXTS': ['.txt'],
    'CHUNK_SIZE': 50,
    'CHUNK_OVERLAP': 0,
    'VECTOR_STORE': {
        'COLLECTION_NAME': 'user_reviews',
        'BATCH_SIZE': 20,
        'ENABLE_HYBRID': True,
    },
    'QUERY': {
        'MODE': 'sparse',
        'SIMILARITY_TOP_K': 3,
        'SPARSE_TOP_K': 3,
    }
}
