from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from models.favorites import FavoriteCity
from services.weather_service import WeatherService
from models import db
from forms import AddFavoriteForm

favorites_bp = Blueprint('favorites', __name__)


@favorites_bp.route('/favorites')
def view_favorites():
    fav_cities = FavoriteCity.query.order_by(FavoriteCity.added_at.desc()).all()

    # Fetch live weather card data for each favorite city
    cards = []
    for fav in fav_cities:
        try:
            w_data = WeatherService.get_weather_by_city(fav.city)
            w_data['fav_id'] = fav.id
            cards.append(w_data)
        except Exception:
            cards.append({
                'fav_id': fav.id,
                'city': fav.city,
                'country': fav.country or '',
                'temp': 'N/A',
                'description': 'Data unavailable',
                'icon': '01d',
            })

    # AddFavoriteForm is passed so the template can render its CSRF token;
    # the form itself is used for CSRF validation on POST submissions.
    form = AddFavoriteForm()
    return render_template('favorites.html', favorites=cards, form=form)


# ------------------------------------------------------------------ #
#  JSON API endpoints — all CSRF-exempted in app.py                  #
# ------------------------------------------------------------------ #

@favorites_bp.route('/api/favorites', methods=['GET', 'POST'])
def api_favorites():
    if request.method == 'GET':
        fav_cities = FavoriteCity.query.order_by(FavoriteCity.added_at.desc()).all()
        return jsonify({'success': True, 'favorites': [f.to_dict() for f in fav_cities]})

    data = request.get_json() or {}
    city = data.get('city', '').strip()
    country = data.get('country', '').strip()

    if not city:
        return jsonify({'success': False, 'error': 'City is required'}), 400

    existing = FavoriteCity.query.filter_by(city=city).first()
    if existing:
        return jsonify({'success': True, 'message': 'City already in favorites', 'is_favorite': True})

    new_fav = FavoriteCity(city=city, country=country)
    db.session.add(new_fav)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Added to favorites',
        'is_favorite': True,
        'favorite': new_fav.to_dict(),
    })


@favorites_bp.route('/api/favorites/toggle', methods=['POST'])
def toggle_favorite():
    data = request.get_json() or {}
    city = data.get('city', '').strip()
    country = data.get('country', '').strip()

    if not city:
        return jsonify({'success': False, 'error': 'City is required'}), 400

    existing = FavoriteCity.query.filter_by(city=city).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({'success': True, 'is_favorite': False, 'message': 'Removed from favorites'})

    new_fav = FavoriteCity(city=city, country=country)
    db.session.add(new_fav)
    db.session.commit()
    return jsonify({'success': True, 'is_favorite': True, 'message': 'Added to favorites'})


@favorites_bp.route('/api/favorites/<int:fav_id>', methods=['DELETE'])
def delete_favorite(fav_id):
    fav = FavoriteCity.query.get(fav_id)
    if not fav:
        return jsonify({'success': False, 'error': 'Favorite not found'}), 404

    db.session.delete(fav)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Favorite removed'})
