from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Open-Meteo API does not require an API key
WEATHER_CODES = {
    0: "Clear Sky",
    1: "Mainly Clear",
    2: "Partly Cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Foggy",
    51: "Light Drizzle",
    53: "Drizzle",
    55: "Heavy Drizzle",
    61: "Light Rain",
    63: "Rain",
    65: "Heavy Rain",
    71: "Light Snow",
    73: "Snow",
    75: "Heavy Snow",
    80: "Rain Showers",
    81: "Rain Showers",
    82: "Heavy Rain Showers",
    95: "Thunderstorm"
}


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/weather")
def weather():
    city = request.args.get("city", "Nashik")

    # Geocoding API
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    geo_params = {
        "name": city,
        "count": 1,
        "language": "en",
        "format": "json"
    }

    geo_response = requests.get(geo_url, params=geo_params)
    geo_data = geo_response.json()

    if "results" not in geo_data:
        return jsonify({"error": "City not found"}), 404

    location = geo_data["results"][0]

    latitude = location["latitude"]
    longitude = location["longitude"]

    # Weather API
    weather_url = "https://api.open-meteo.com/v1/forecast"

    weather_params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "is_day",
            "precipitation",
            "weather_code",
            "wind_speed_10m"
        ],
        "daily": [
            "weather_code",
            "temperature_2m_max",
            "temperature_2m_min",
            "sunrise",
            "sunset"
        ],
        "timezone": "auto",
        "forecast_days": 7
    }

    response = requests.get(weather_url, params=weather_params)
    data = response.json()

    current = data["current"]
    daily = data["daily"]

    forecast = []

    for i in range(7):
        forecast.append({
            "date": daily["time"][i],
            "weather": WEATHER_CODES.get(
                daily["weather_code"][i],
                "Unknown"
            ),
            "max_temp": daily["temperature_2m_max"][i],
            "min_temp": daily["temperature_2m_min"][i]
        })

    result = {
        "city": location["name"],
        "country": location.get("country", ""),
        "temperature": current["temperature_2m"],
        "feels_like": current["apparent_temperature"],
        "humidity": current["relative_humidity_2m"],
        "wind_speed": current["wind_speed_10m"],
        "precipitation": current["precipitation"],
        "weather": WEATHER_CODES.get(
            current["weather_code"],
            "Unknown"
        ),
        "is_day": current["is_day"],
        "sunrise": daily["sunrise"][0],
        "sunset": daily["sunset"][0],
        "forecast": forecast
    }

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
