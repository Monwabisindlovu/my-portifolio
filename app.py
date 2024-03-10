from flask import Flask, render_template, request
import requests
import json
import datetime

app = Flask(__name__)

# Register the custom 'datetime' filter
app.jinja_env.filters['datetime'] = datetime.datetime.utcfromtimestamp

# Updated API key for WeatherAPI
WEATHER_API_KEY = "ff0f07d8a8d446ef8b084913241003"

def get_weather_data(location):
    base_url = "http://api.weatherapi.com/v1/forecast.json"
    complete_url = f"{base_url}?key={WEATHER_API_KEY}&q={location}&days=5&aqi=no&alerts=no"  # Fetching 5 days forecast
    response = requests.get(complete_url)
    data = response.json()

    if 'error' not in data:
        current = data['current']
        forecast_days = data['forecast']['forecastday']

        # Fetch hourly forecast for the current day
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        hourly_forecast = []
        for forecast in forecast_days:
            if forecast['date'] == current_date:
                hourly_forecast = forecast['hour']
                break

        daily_forecast = []

        for forecast in forecast_days:
            day_forecast = {
                "date": forecast['date'],
                "max_temp": forecast['day']['maxtemp_c'],
                "min_temp": forecast['day']['mintemp_c'],
                "weather_description": forecast['day']['condition']['text'],
                "icon": forecast['day']['condition']['icon'],
            }
            daily_forecast.append(day_forecast)

        weather = {
            "current": {
                "temperature": current['temp_c'],  # Temperature in Celsius
                "humidity": current['humidity'],  # Humidity percentage
                "weather_description": current['condition']['text'],  # Description of weather condition
                "icon": current['condition']['icon'],  # Weather icon code
                "latitude": data['location']['lat'],  # Latitude of the location
                "longitude": data['location']['lon'],  # Longitude of the location
                "wind_speed": current['wind_kph'],  # Wind speed in kilometers per hour
                "hourly_forecast": hourly_forecast
            },
            "daily_forecast": daily_forecast
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
        location = f"{location},{location}"
        weather_data = get_weather_data(location)
        if weather_data is None:
            error = "Location not found. Please try again."
    return render_template('index.html', weather_data=weather_data, error=error, current_time=datetime.datetime.now())

if __name__ == '__main__':
    app.run(debug=True)