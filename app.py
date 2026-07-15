from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# Replace with your actual OpenWeather API key
API_KEY = "YOUR_OPENWEATHER_API_KEY"


@app.route("/", methods=["GET", "POST"])
def home():
    weather = None
    error = None

    if request.method == "POST":
        city = request.form.get("city")

        if not city:
            error = "Please enter a city name."
        else:
            url = "https://api.openweathermap.org/data/2.5/weather"

            params = {
                "q": city,
                "appid": API_KEY,
                "units": "metric"
            }

            try:
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()

                weather = {
                    "city": data["name"],
                    "country": data["sys"]["country"],
                    "temp": data["main"]["temp"],
                    "humidity": data["main"]["humidity"],
                    "wind": data["wind"]["speed"],
                    "condition": data["weather"][0]["main"],
                    "description": data["weather"][0]["description"].title(),
                    "icon": data["weather"][0]["icon"]
                }

            except requests.exceptions.HTTPError:
                error = "City not found."
            except requests.exceptions.RequestException:
                error = "Unable to connect to the weather service."
            except KeyError:
                error = "Unexpected response from the weather service."

    return render_template("index.html", weather=weather, error=error)


if __name__ == "__main__":
    app.run(debug=True)