# 🌤️ WeatherSphere — Production-Ready SaaS Weather Platform

**WeatherSphere** is a premium, full-featured meteorological analytics platform built using Python Flask, SQLAlchemy ORM, Bootstrap 5, Chart.js, and the Visual Crossing Weather API.


---

## ✨ Features

- 🌡️ **Real-Time Weather Metrics**: Current temperature, Feels like, Min/Max temp, Humidity, Pressure, Wind Speed & Direction, Visibility, Cloudiness, Sunrise & Sunset.
- 🌫️ **Air Quality Index (AQI)**: Live PM2.5, PM10, NO2 air pollution reporting.
- ☀️ **UV Index Indicator**: Solar radiation level indicators with health alerts.
- 📅 **5-Day & 24-Hour Hourly Forecast**: Interactive scrollable hourly forecast and daily projections.
- 📊 **Interactive Weather Trends**: Chart.js data visualizations for Temperature, Humidity, and Wind speed trends.
- 🤖 **AI Weather Recommendations**: Automatic lifestyle tips on attire, umbrella necessity, and outdoor safety based on live conditions.
- ⚔️ **City Weather Comparison**: Side-by-side weather comparisons between multiple world cities.
- 📍 **Browser Geolocation**: Single-click "Detect My Location" weather fetching.
- ⭐ **Favorites & History Management**: Save favorite cities and track search history using SQLite & SQLAlchemy.
- 🎨 **Dynamic Glassmorphic Theme & Dark Mode**: Dynamic backgrounds that automatically adapt to weather conditions (Sunny, Rain, Snow, Clouds, Night) with LocalStorage theme persistence.
- ⚡ **Flask-Caching**: 10-minute caching layer to prevent API rate limits and optimize response times.

---

## 📁 Folder Structure

```
weather-dashboard/
├── app.py                   # Application Factory & Entry point
├── config.py                # Environment configuration
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variable template
├── .env                     # Local environment file
├── README.md                # Project documentation
├── instance/
│   └── database.db          # SQLite Database (auto-generated)
├── models/
│   ├── __init__.py
│   ├── history.py           # SearchHistory SQLAlchemy Model
│   └── favorites.py         # FavoriteCity SQLAlchemy Model
├── services/
│   ├── __init__.py
│   ├── weather_service.py   # OpenWeatherMap API integration & fallback logic
│   └── cache_service.py     # Flask-Caching instance
├── routes/
│   ├── __init__.py
│   ├── weather.py           # Home, Dashboard, API routes
│   ├── history.py           # Search History routes
│   └── favorites.py         # Favorites routes
├── templates/
│   ├── base.html            # Base Jinja layout
│   ├── home.html            # Hero landing page
│   ├── dashboard.html       # Analytics dashboard
│   ├── history.html         # History page
│   ├── favorites.html       # Favorites page
│   ├── 404.html             # 404 error page
│   ├── 500.html             # 500 error page
│   └── components/
│       ├── navbar.html
│       ├── footer.html
│       ├── weather_cards.html
│       └── forecast_cards.html
└── static/
    ├── css/
    │   ├── style.css        # Base design system & glassmorphism
    │   ├── dashboard.css    # Dashboard styles
    │   └── animations.css   # Keyframe animations & spinners
    └── js/
        ├── main.js          # Geolocation, AJAX & modal logic
        ├── weather.js       # Background updater & live preview
        ├── theme.js         # Light/Dark mode switcher
        └── charts.js        # Chart.js visualization logic
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.9+
- Visual Crossing Weather API Key (Get a free key at [Visual Crossing Weather API](https://www.visualcrossing.com/weather-api))

### 2. Installation

1. **Clone or navigate to the project directory**:
   ```bash
   cd "c:\Users\asus\OneDrive\Documents\LPU\Summer pep\Project"
   ```

2. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   Copy `.env.example` to `.env` and enter your Visual Crossing Weather API key:
   ```env
   VISUALCROSSING_API_KEY=your_actual_api_key_here
   SECRET_KEY=weathersphere-secret-key
   FLASK_ENV=development
   ```

5. **Run the Application**:
   ```bash
   python app.py
   ```
   Open your browser and navigate to `http://localhost:5000`.

---

## 🛡️ Error Handling & Fallbacks

- If `VISUALCROSSING_API_KEY` is missing or invalid, the app gracefully transitions to **Demo Mode**, serving structured mock weather data so you can test and demonstrate the UI without interruption.

- Network timeouts, 404 city errors, and rate limits are handled with user-friendly glass alerts.

---

## 🔮 Future Improvements

- 🔔 Push Notifications for severe weather alerts.
- 🗺️ Interactive Leaflet/Mapbox radar map overlay.
- 👤 User authentication (OAuth / JWT) for multi-tenant favorite profiles.
