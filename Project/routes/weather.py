from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from services.weather_service import WeatherService
from models.history import SearchHistory
from models.favorites import FavoriteCity
from models import db
from forms import CitySearchForm

weather_bp = Blueprint('weather', __name__)


@weather_bp.route('/', methods=['GET', 'POST'])
def home():
    form = CitySearchForm()

    # Handle WTForms POST submission (form rendered with method="POST")
    if form.validate_on_submit():
        return redirect(url_for('weather.dashboard', city=form.city.data.strip()))

    popular_cities = ['London', 'New York', 'Tokyo', 'Paris', 'Sydney', 'Delhi']
    recent_searches = SearchHistory.query.order_by(SearchHistory.created_at.desc()).limit(5).all()
    favorites = FavoriteCity.query.order_by(FavoriteCity.added_at.desc()).limit(6).all()
    return render_template(
        'home.html',
        form=form,
        popular_cities=popular_cities,
        recent_searches=recent_searches,
        favorites=favorites,
    )


@weather_bp.route('/dashboard')
def dashboard():
    city = request.args.get('city', 'New York')
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)

    try:
        if lat is not None and lon is not None:
            weather_data = WeatherService.get_weather_by_coords(lat, lon)
        else:
            weather_data = WeatherService.get_weather_by_city(city)

        # Record in Search History (delete existing entry first to avoid duplicates)
        if weather_data and 'city' in weather_data:
            SearchHistory.query.filter_by(city=weather_data['city']).delete()
            history_item = SearchHistory(
                city=weather_data['city'],
                country=weather_data.get('country', ''),
                temperature=weather_data['temp'],
                weather=weather_data['description'],
                icon=weather_data['icon'],
            )
            db.session.add(history_item)
            db.session.commit()

        # Check if city is already favorited
        is_favorite = False
        if weather_data and 'city' in weather_data:
            is_favorite = FavoriteCity.query.filter_by(city=weather_data['city']).first() is not None

        return render_template('dashboard.html', weather=weather_data, is_favorite=is_favorite)

    except ValueError as ve:
        flash(str(ve), 'warning')
        return redirect(url_for('weather.home'))
    except Exception as e:
        flash(f"Unable to fetch weather data: {str(e)}", 'danger')
        return redirect(url_for('weather.home'))


# ------------------------------------------------------------------ #
#  JSON API endpoints — all exempted from CSRF in app.py             #
#  (our JS sends X-CSRFToken header; external callers don't need it) #
# ------------------------------------------------------------------ #

@weather_bp.route('/api/weather', methods=['GET', 'POST'])
def api_weather():
    if request.method == 'POST':
        data = request.get_json() or {}
        city = data.get('city')
    else:
        city = request.args.get('city')

    if not city:
        return jsonify({'error': 'City parameter is required'}), 400

    try:
        weather_data = WeatherService.get_weather_by_city(city)
        SearchHistory.query.filter_by(city=weather_data['city']).delete()
        history_item = SearchHistory(
            city=weather_data['city'],
            country=weather_data.get('country', ''),
            temperature=weather_data['temp'],
            weather=weather_data['description'],
            icon=weather_data['icon'],
        )
        db.session.add(history_item)
        db.session.commit()

        is_favorite = FavoriteCity.query.filter_by(city=weather_data['city']).first() is not None
        weather_data['is_favorite'] = is_favorite

        return jsonify({'success': True, 'data': weather_data})
    except ValueError as ve:
        return jsonify({'success': False, 'error': str(ve)}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@weather_bp.route('/api/weather/coords', methods=['POST'])
def api_weather_coords():
    data = request.get_json() or {}
    lat = data.get('lat')
    lon = data.get('lon')

    if lat is None or lon is None:
        return jsonify({'error': 'Latitude and longitude parameters are required'}), 400

    try:
        weather_data = WeatherService.get_weather_by_coords(float(lat), float(lon))
        SearchHistory.query.filter_by(city=weather_data['city']).delete()
        history_item = SearchHistory(
            city=weather_data['city'],
            country=weather_data.get('country', ''),
            temperature=weather_data['temp'],
            weather=weather_data['description'],
            icon=weather_data['icon'],
        )
        db.session.add(history_item)
        db.session.commit()

        is_favorite = FavoriteCity.query.filter_by(city=weather_data['city']).first() is not None
        weather_data['is_favorite'] = is_favorite

        return jsonify({'success': True, 'data': weather_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@weather_bp.route('/api/compare')
def api_compare():
    cities_param = request.args.get('cities', 'Delhi,Mumbai,London')
    city_list = [c.strip() for c in cities_param.split(',') if c.strip()][:4]  # max 4

    results = []
    for city in city_list:
        try:
            w = WeatherService.get_weather_by_city(city)
            results.append(w)
        except Exception:
            pass

    return jsonify({'success': True, 'comparison': results})


@weather_bp.route('/api/cities/search')
def api_city_search():
    query = request.args.get('q', '').strip()
    if len(query) < 2:
        return jsonify({'success': True, 'results': []})

    try:
        suggestions = WeatherService.search_cities(query)
        return jsonify({'success': True, 'results': suggestions})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'results': []})
