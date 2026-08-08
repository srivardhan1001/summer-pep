import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'), override=True)


def _get_database_url():
    """
    Return the database URI, normalising the legacy 'postgres://' scheme that
    Heroku / Render emit to the 'postgresql://' scheme required by SQLAlchemy 1.4+.
    Falls back to a local SQLite file for development convenience when no
    DATABASE_URL is set.
    """
    uri = os.environ.get('DATABASE_URL')
    if uri:
        # SQLAlchemy dropped support for the old postgres:// dialect prefix
        if uri.startswith('postgres://'):
            uri = uri.replace('postgres://', 'postgresql://', 1)
        return uri
    # Local SQLite fallback — useful when no PostgreSQL is configured yet
    return 'sqlite:///' + os.path.join(basedir, 'instance', 'database.db')


class Config:
    # ------------------------------------------------------------------ #
    #  Security                                                            #
    # ------------------------------------------------------------------ #
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'weathersphere-secret-key-default-dev'

    # ------------------------------------------------------------------ #
    #  Flask-WTF / CSRF                                                   #
    # ------------------------------------------------------------------ #
    WTF_CSRF_ENABLED = True
    # CSRF token expires after 1 hour (configurable via env var)
    WTF_CSRF_TIME_LIMIT = int(os.environ.get('WTF_CSRF_TIME_LIMIT', 3600))
    # Allow CSRF tokens to be read from the X-CSRFToken request header
    # so our fetch() AJAX calls can pass the token without a hidden field.
    WTF_CSRF_CHECK_DEFAULT = True

    # ------------------------------------------------------------------ #
    #  Database                                                           #
    # ------------------------------------------------------------------ #
    SQLALCHEMY_DATABASE_URI = _get_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ------------------------------------------------------------------ #
    #  Visual Crossing Weather API                                        #
    # ------------------------------------------------------------------ #
    VISUALCROSSING_API_KEY = (
        os.environ.get('VISUALCROSSING_API_KEY')
        or os.environ.get('OPENWEATHER_API_KEY')
        or ''
    )
    VISUALCROSSING_BASE_URL = (
        'https://weather.visualcrossing.com/VisualCrossingWebServices'
        '/rest/services/timeline'
    )

    # ------------------------------------------------------------------ #
    #  Caching (SimpleCache = in-process memory, suitable for single      #
    #  process deployments; swap to Redis for multi-worker prod)          #
    # ------------------------------------------------------------------ #
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 600  # 10 minutes


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    # Enforce a strong secret key in production
    WTF_CSRF_SSL_STRICT = True


config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
