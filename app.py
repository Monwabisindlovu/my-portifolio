from flask import Flask, render_template, request
import requests
import json
import datetime

app = Flask(__name__)

# Register the custom 'datetime' filter
app.jinja_env.filters['datetime'] = datetime.datetime.utcfromtimestamp

def get_weather_data(location):
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}appid=6e801847a6d6f830b53dbd1ac530135f&q={location}"
    response = requests.get(complete_url)
    data = response.json()

    if data["cod"] != "404":
        temp_data = data["main"]
        weather_data = data["weather"][0]
        latitude = data["coord"]["lat"]
        longitude = data["coord"]["lon"]

        weather = {
            # Use 'feels_like' directly, and subtract 273.15
            "temperature": round(temp_data["feels_like"] - 273.15, 2),  # Round temperature to 2 decimal places
            "humidity": temp_data["humidity"],
            "weather_description": weather_data["description"],
            "icon": weather_data["icon"],
            "latitude": latitude,
            "longitude": longitude,
            "wind_speed": data["wind"]["speed"],
        }

        return weather
    else:
        return None


@app.route('/', methods=['GET', 'POST'])
def index_post():
    weather_data = None
    error = None
    if request.method == 'POST':
        location = request.form['location']
        location = request.form['location']
        location = f"{location},{location}"
        weather_data = get_weather_data(location)
        if weather_data is None:
            error = "Location not found. Please try again."
    return render_template('index.html', weather_data=weather_data, error=error, current_time=datetime.datetime.now())

if __name__ == '__main__':
    app.run(debug=True)
