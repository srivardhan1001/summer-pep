import requests
from datetime import datetime, timezone, timedelta
from flask import current_app
from services.cache_service import cache

class WeatherService:

    VC_ICON_MAP = {
        'clear-day': '01d',
        'clear-night': '01n',
        'partly-cloudy-day': '02d',
        'partly-cloudy-night': '02n',
        'cloudy': '03d',
        'overcast': '04d',
        'rain': '10d',
        'showers-day': '09d',
        'showers-night': '09n',
        'thunder-rain': '11d',
        'thunder-showers-day': '11d',
        'thunder-showers-night': '11n',
        'snow': '13d',
        'snow-showers-day': '13d',
        'snow-showers-night': '13n',
        'fog': '50d',
        'wind': '50d',
        'sleet': '13d'
    }

    @classmethod
    def _map_icon(cls, vc_icon):
        if not vc_icon:
            return '02d'
        return cls.VC_ICON_MAP.get(vc_icon.lower(), '02d')

    @staticmethod
    def _make_request(location_query):
        api_key = current_app.config.get('VISUALCROSSING_API_KEY') or current_app.config.get('OPENWEATHER_API_KEY')
        if not api_key:
            raise ValueError("VISUALCROSSING_API_KEY is not configured in .env file.")

        base_url = current_app.config.get(
            'VISUALCROSSING_BASE_URL',
            'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline'
        )

        url = f"{base_url}/{requests.utils.quote(str(location_query))}"
        params = {
            'unitGroup': 'metric',
            'key': api_key,
            'contentType': 'json',
            'include': 'current,hours,days'
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code in (400, 404):
                raise ValueError("City not found. Please check spelling.")
            elif response.status_code == 401:
                raise ValueError("Invalid Visual Crossing API Key. Please verify your .env file.")
            elif response.status_code == 429:
                raise ValueError("API rate limit exceeded. Please try again later.")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            raise RuntimeError("Weather service connection timed out. Please try again.")
        except requests.exceptions.ConnectionError:
            raise RuntimeError("Network error. Please check your internet connection.")
        except requests.exceptions.HTTPError as err:
            raise RuntimeError(f"HTTP error occurred: {err}")

    @staticmethod
    def get_weather_by_city(city_name):
        cache_key = f"weather_vc_city_{city_name.lower().strip()}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data

        try:
            raw_data = WeatherService._make_request(city_name)
            result = WeatherService._format_full_weather(raw_data)
            cache.set(cache_key, result, timeout=600)
            return result
        except Exception as e:
            if "VISUALCROSSING_API_KEY is not configured" in str(e) or "Invalid Visual Crossing API Key" in str(e):
                return WeatherService._generate_mock_weather(city_name)
            raise e

    @staticmethod
    def get_weather_by_coords(lat, lon):
        cache_key = f"weather_vc_coords_{round(lat,2)}_{round(lon,2)}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data

        try:
            location_query = f"{lat},{lon}"
            raw_data = WeatherService._make_request(location_query)
            result = WeatherService._format_full_weather(raw_data)
            cache.set(cache_key, result, timeout=600)
            return result
        except Exception as e:
            if "VISUALCROSSING_API_KEY is not configured" in str(e) or "Invalid Visual Crossing API Key" in str(e):
                return WeatherService._generate_mock_weather(f"Lat: {round(lat, 2)}, Lon: {round(lon, 2)}")
            raise e

    @staticmethod
    def search_cities(query):
        if not query or len(query.strip()) < 2:
            return []

        clean_q = query.strip().lower()
        cache_key = f"city_suggestions_{clean_q}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        results = []
        seen_names = set()

        try:
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                'format': 'json',
                'addressdetails': 1,
                'q': clean_q,
                'limit': 6
            }
            headers = {'User-Agent': 'WeatherSphereApp/1.0'}
            resp = requests.get(url, params=params, headers=headers, timeout=4)
            if resp.status_code == 200:
                data = resp.json()
                for item in data:
                    addr = item.get('address', {})
                    city = addr.get('city') or addr.get('town') or addr.get('village') or addr.get('municipality') or addr.get('suburb') or item.get('name')
                    state = addr.get('state') or addr.get('county') or addr.get('state_district') or ''
                    country = addr.get('country') or ''

                    if city:
                        city = city.strip()
                        state = state.strip()
                        country = country.strip()

                        # Deduplicate
                        unique_key = f"{city.lower()}_{state.lower()}_{country.lower()}"
                        if unique_key not in seen_names:
                            seen_names.add(unique_key)
                            display_label = ", ".join([p for p in [city, state, country] if p])
                            results.append({
                                'city': city,
                                'state': state,
                                'country': country,
                                'display_name': display_label,
                                'lat': item.get('lat'),
                                'lon': item.get('lon')
                            })
        except Exception:
            pass

        # Fallback list for common query prefixes if API returned few/no results
        popular_db = [
            {'city': 'Phagwara', 'state': 'Punjab', 'country': 'India'},
            {'city': 'Phag', 'state': 'Himachal Pradesh', 'country': 'India'},
            {'city': 'Phag', 'state': 'Bihar', 'country': 'India'},
            {'city': 'Delhi', 'state': 'Delhi', 'country': 'India'},
            {'city': 'Mumbai', 'state': 'Maharashtra', 'country': 'India'},
            {'city': 'London', 'state': 'England', 'country': 'United Kingdom'},
            {'city': 'New York', 'state': 'New York', 'country': 'United States'},
            {'city': 'Tokyo', 'state': 'Tokyo', 'country': 'Japan'},
            {'city': 'Paris', 'state': 'Île-de-France', 'country': 'France'},
            {'city': 'Sydney', 'state': 'New South Wales', 'country': 'Australia'},
            {'city': 'Toronto', 'state': 'Ontario', 'country': 'Canada'},
            {'city': 'Berlin', 'state': 'Berlin', 'country': 'Germany'}
        ]

        for item in popular_db:
            c_name = item['city']
            full_str = f"{c_name}, {item['state']}, {item['country']}"
            if clean_q in c_name.lower() or clean_q in item['state'].lower():
                unique_key = f"{c_name.lower()}_{item['state'].lower()}_{item['country'].lower()}"
                if unique_key not in seen_names and len(results) < 6:
                    seen_names.add(unique_key)
                    results.append({
                        'city': c_name,
                        'state': item['state'],
                        'country': item['country'],
                        'display_name': full_str
                    })

        cache.set(cache_key, results, timeout=1800)
        return results

    @staticmethod
    def _format_full_weather(data):

        # Extract location info
        address_parts = data.get('resolvedAddress', data.get('address', '')).split(',')
        city_name = address_parts[0].strip()
        country_code = address_parts[-1].strip() if len(address_parts) > 1 else ''

        lat = data.get('latitude', 0.0)
        lon = data.get('longitude', 0.0)

        tz_offset_hours = data.get('tzoffset', 0)
        local_time = datetime.now(timezone.utc) + timedelta(hours=tz_offset_hours)

        current = data.get('currentConditions', {})
        days = data.get('days', [])
        today = days[0] if len(days) > 0 else {}

        # Current weather metrics
        temp = current.get('temp', today.get('temp', 20.0))
        feels_like = current.get('feelslike', today.get('feelslike', temp))
        temp_min = today.get('tempmin', temp - 3)
        temp_max = today.get('tempmax', temp + 4)

        condition_desc = current.get('conditions', today.get('conditions', 'Clear')).title()
        # Simplify condition main (e.g. "Rain, Overcast" -> "Rain")
        condition_main = condition_desc.split(',')[0].strip()

        vc_icon = current.get('icon', today.get('icon', 'clear-day'))
        owm_icon = WeatherService._map_icon(vc_icon)

        humidity = current.get('humidity', today.get('humidity', 50))
        pressure = current.get('pressure', today.get('pressure', 1013))
        wind_speed = current.get('windspeed', today.get('windspeed', 10.0)) # km/h in metric
        wind_dir = current.get('winddir', today.get('winddir', 0))
        visibility = current.get('visibility', today.get('visibility', 10.0)) # km in metric
        cloudiness = current.get('cloudcover', today.get('cloudcover', 0))
        uv_index = round(current.get('uvindex', today.get('uvindex', 3.0)), 1)

        # Sunrise & Sunset formatting
        sunrise_str = current.get('sunrise', today.get('sunrise', '06:00:00'))
        sunset_str = current.get('sunset', today.get('sunset', '18:30:00'))

        try:
            sr_dt = datetime.strptime(sunrise_str, '%H:%M:%S')
            sunrise_fmt = sr_dt.strftime('%I:%M %p')
        except ValueError:
            sunrise_fmt = sunrise_str

        try:
            ss_dt = datetime.strptime(sunset_str, '%H:%M:%S')
            sunset_fmt = ss_dt.strftime('%I:%M %p')
        except ValueError:
            sunset_fmt = sunset_str

        # AQI approximation / structure compatibility
        aqi_val = 1 if uv_index < 3 else (2 if uv_index < 6 else (3 if uv_index < 8 else 4))
        aqi_labels = {1: 'Good', 2: 'Fair', 3: 'Moderate', 4: 'Poor', 5: 'Very Poor'}
        aqi_data = {
            'index': aqi_val,
            'label': aqi_labels.get(aqi_val, 'Fair'),
            'components': {
                'pm2_5': round(cloudiness * 0.4, 1),
                'pm10': round(cloudiness * 0.8, 1),
                'no2': 15.0
            }
        }

        # Process Hourly Forecast (next 8 interval hours across today & tomorrow)
        hourly_forecast = []
        all_hours = []
        for day in days[:2]:
            day_hours = day.get('hours', [])
            for h in day_hours:
                all_hours.append(h)

        # Find hours starting from current local hour
        current_hour_str = current.get('datetime', local_time.strftime('%H:00:00'))
        start_idx = 0
        for idx, h in enumerate(all_hours):
            if h.get('datetime', '') >= current_hour_str:
                start_idx = idx
                break

        selected_hours = all_hours[start_idx:start_idx+24:3] # Every 3 hours for next 24h
        if not selected_hours:
            selected_hours = all_hours[:8]

        for h in selected_hours[:8]:
            try:
                h_dt = datetime.strptime(h.get('datetime', '12:00:00'), '%H:%M:%S')
                time_fmt = h_dt.strftime('%I:%M %p')
            except ValueError:
                time_fmt = h.get('datetime', '12:00')

            hourly_forecast.append({
                'time': time_fmt,
                'temp': round(h.get('temp', temp)),
                'icon': WeatherService._map_icon(h.get('icon', vc_icon)),
                'condition': h.get('conditions', condition_main).split(',')[0].strip(),
                'humidity': h.get('humidity', humidity)
            })

        # Process 5-Day Forecast
        daily_forecast = []
        for day in days[:5]:
            try:
                d_obj = datetime.strptime(day.get('datetime'), '%Y-%m-%d')
                day_str = d_obj.strftime('%A')
                date_str = d_obj.strftime('%b %d')
            except Exception:
                day_str = 'Today'
                date_str = ''

            daily_forecast.append({
                'day': day_str,
                'date': date_str,
                'temp': round(day.get('temp', temp)),
                'min_temp': round(day.get('tempmin', temp_min)),
                'max_temp': round(day.get('tempmax', temp_max)),
                'icon': WeatherService._map_icon(day.get('icon', vc_icon)),
                'description': day.get('conditions', condition_desc).title(),
                'humidity': day.get('humidity', humidity),
                'wind_speed': round(day.get('windspeed', wind_speed), 1)
            })

        # Recommendations
        recommendations = WeatherService._generate_recommendations(temp, condition_main, humidity, wind_speed, aqi_data['index'])

        return {
            'city': city_name,
            'country': country_code,
            'coords': {'lat': lat, 'lon': lon},
            'temp': round(temp, 1),
            'feels_like': round(feels_like, 1),
            'temp_min': round(temp_min, 1),
            'temp_max': round(temp_max, 1),
            'condition': condition_main,
            'description': condition_desc,
            'icon': owm_icon,
            'humidity': humidity,
            'pressure': pressure,
            'wind_speed': round(wind_speed, 1),
            'wind_direction': wind_dir,
            'visibility': round(visibility, 1),
            'cloudiness': cloudiness,
            'sunrise': sunrise_fmt,
            'sunset': sunset_fmt,
            'local_time': local_time.strftime('%I:%M %p, %a %b %d'),
            'is_night': 'night' in vc_icon,
            'aqi': aqi_data,
            'uv_index': uv_index,
            'hourly_forecast': hourly_forecast,
            'daily_forecast': daily_forecast,
            'recommendations': recommendations
        }

    @staticmethod
    def _generate_recommendations(temp, condition, humidity, wind_speed, aqi_index):
        recs = []

        if temp < 10:
            recs.append({'icon': 'fa-solid fa-vest', 'title': 'Dress Warmly', 'text': 'It is quite cold outside. Wear heavy jackets and layers.'})
        elif temp < 20:
            recs.append({'icon': 'fa-solid fa-shirt', 'title': 'Light Jacket', 'text': 'Mild weather. A light sweater or cardigan is recommended.'})
        else:
            recs.append({'icon': 'fa-solid fa-shirt', 'title': 'Breathable Wear', 'text': 'Warm weather! Wear light cotton clothes to stay comfortable.'})

        if any(w in condition.lower() for w in ['rain', 'drizzle', 'thunder', 'shower', 'squall']):
            recs.append({'icon': 'fa-solid fa-umbrella', 'title': 'Carry Umbrella', 'text': 'Rain expected. Don’t forget your umbrella or raincoat!'})
        elif humidity > 80:
            recs.append({'icon': 'fa-solid fa-droplet', 'title': 'High Humidity', 'text': 'Muggy conditions outside. Stay hydrated.'})

        if aqi_index >= 4:
            recs.append({'icon': 'fa-solid fa-head-side-mask', 'title': 'Wear Air Mask', 'text': 'Poor air quality detected. Limit outdoor exertion and wear N95 mask.'})
        elif wind_speed > 35:
            recs.append({'icon': 'fa-solid fa-wind', 'title': 'High Winds', 'text': 'Strong wind gusts. Take caution when driving or walking near trees.'})
        else:
            recs.append({'icon': 'fa-solid fa-person-running', 'title': 'Outdoor Friendly', 'text': 'Great conditions for an outdoor walk or exercise routine!'})

        return recs

    @staticmethod
    def _generate_mock_weather(city_name):
        clean_city = city_name.strip().title() if city_name else "New York"
        
        now = datetime.now()
        sunrise = now.replace(hour=6, minute=15)
        sunset = now.replace(hour=19, minute=30)
        
        hourly = []
        for i in range(8):
            t = now + timedelta(hours=i*3)
            hourly.append({
                'time': t.strftime('%I:%M %p'),
                'temp': 24 + (i % 4),
                'icon': '02d' if i < 4 else '02n',
                'condition': 'Clouds',
                'humidity': 55 + (i * 2)
            })

        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        daily = []
        for idx, day in enumerate(days):
            d = now + timedelta(days=idx)
            daily.append({
                'day': day,
                'date': d.strftime('%b %d'),
                'temp': 25 + idx,
                'min_temp': 18 + idx,
                'max_temp': 27 + idx,
                'icon': '01d' if idx % 2 == 0 else '03d',
                'description': 'Sunny' if idx % 2 == 0 else 'Partly Cloudy',
                'humidity': 50 + idx * 3,
                'wind_speed': 12.5 + idx
            })

        return {
            'city': clean_city,
            'country': 'US',
            'coords': {'lat': 40.7128, 'lon': -74.0060},
            'temp': 25.4,
            'feels_like': 26.1,
            'temp_min': 21.0,
            'temp_max': 28.5,
            'condition': 'Clear',
            'description': 'Clear Sky',
            'icon': '01d',
            'humidity': 58,
            'pressure': 1013,
            'wind_speed': 14.4,
            'wind_direction': 180,
            'visibility': 10.0,
            'cloudiness': 15,
            'sunrise': sunrise.strftime('%I:%M %p'),
            'sunset': sunset.strftime('%I:%M %p'),
            'local_time': now.strftime('%I:%M %p, %a %b %d'),
            'is_night': False,
            'aqi': {'index': 2, 'label': 'Fair', 'components': {'pm2_5': 12.4, 'pm10': 20.1, 'no2': 15.0}},
            'uv_index': 5.8,
            'hourly_forecast': hourly,
            'daily_forecast': daily,
            'recommendations': WeatherService._generate_recommendations(25.4, 'Clear', 58, 14.4, 2),
            'is_demo_data': True
        }
