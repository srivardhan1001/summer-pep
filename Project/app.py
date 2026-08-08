import os
from flask import Flask, render_template
from config import config_by_name
from models import db
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from services.cache_service import cache

# Module-level CSRFProtect so routes can import `csrf` to exempt specific
# endpoints (e.g. pure JSON APIs consumed by external clients).
csrf = CSRFProtect()


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))

    # Ensure instance folder exists (needed for SQLite fallback in dev)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # ------------------------------------------------------------------ #
    #  Initialize Extensions                                              #
    # ------------------------------------------------------------------ #
    db.init_app(app)
    Migrate(app, db)
    cache.init_app(app)

    # CSRF protection — must be initialised after app config is loaded so
    # it picks up SECRET_KEY and WTF_CSRF_* settings from config.py.
    csrf.init_app(app)

    # ------------------------------------------------------------------ #
    #  Register Blueprints                                                #
    # ------------------------------------------------------------------ #
    from routes.weather import weather_bp
    from routes.history import history_bp
    from routes.favorites import favorites_bp

    app.register_blueprint(weather_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(favorites_bp)

    # ------------------------------------------------------------------ #
    #  CSRF exemptions for pure JSON API endpoints                        #
    #                                                                     #
    #  These routes are called by our own JS (which sends the token via   #
    #  X-CSRFToken header — handled by Flask-WTF automatically) AND may   #
    #  be called by external tools / Postman during development.          #
    #  Exempting them keeps the API usable without a browser session      #
    #  while the HTML pages remain fully CSRF-protected.                  #
    # ------------------------------------------------------------------ #
    from routes.weather import (
        api_weather, api_weather_coords, api_compare, api_city_search
    )
    from routes.favorites import api_favorites, toggle_favorite, delete_favorite
    from routes.history import get_history_api, delete_history_item, clear_all_history

    for view_func in [
        api_weather,
        api_weather_coords,
        api_compare,
        api_city_search,
        api_favorites,
        toggle_favorite,
        delete_favorite,
        get_history_api,
        delete_history_item,
        clear_all_history,
    ]:
        csrf.exempt(view_func)

    # ------------------------------------------------------------------ #
    #  Global Error Handlers                                              #
    # ------------------------------------------------------------------ #
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    # ------------------------------------------------------------------ #
    #  Database                                                           #
    #                                                                     #
    #  For PostgreSQL use Flask-Migrate:                                  #
    #    flask db init        (first time only)                           #
    #    flask db migrate -m "initial schema"                             #
    #    flask db upgrade                                                 #
    #                                                                     #
    #  create_all() is kept here only as a convenience for the SQLite    #
    #  development fallback so the app boots without running migrations.  #
    #  When DATABASE_URL points to PostgreSQL, rely on `flask db upgrade` #
    #  and this call becomes a no-op for already-existing tables.         #
    # ------------------------------------------------------------------ #
    with app.app_context():
        uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if uri.startswith('sqlite'):
            db.create_all()
        # For PostgreSQL: run `flask db upgrade` instead

    return app


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
