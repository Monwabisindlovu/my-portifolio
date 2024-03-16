from flask import Flask, render_template, request
import requests
import json
import datetime

app = Flask(__name__)

# Register the custom 'datetime' filter
app.jinja_env.filters['datetime'] = datetime.datetime.utcfromtimestamp

# Updated API key for WeatherAPI
WEATHER_API_KEY = "ff0f07d8a8d446ef8b084913241003"

""" Function to generate personalized recommendations and warnings based on weather data """
def generate_recommendations_and_warnings(weather_data):
    recommendations = []
    warnings = []

    """ Example: If it's sunny and warm, recommend outdoor activities """
    current_weather = weather_data['current']['weather_description']
    current_temperature = weather_data['current']['temperature']

    if "sunny" in current_weather.lower() and current_temperature > 20:
        recommendations.append("It's a sunny day! Perfect for outdoor activities like hiking or picnics.")

    """ Generate warnings based on weather conditions """
    if current_temperature > 30:
        warnings.append("It's very hot outside. Stay hydrated and avoid prolonged exposure to the sun.")
    elif current_temperature < 10:
        warnings.append("It's very cold outside. Make sure to wear warm clothing.")

    """ Check for heavy rain """
    if "rain" in current_weather.lower():
        warnings.append("Heavy rain is expected. Carry an umbrella or raincoat.")

    """ Check for strong winds """"
    wind_speed = weather_data['current']['wind_speed']
    if wind_speed > 30:
        warnings.append("Strong winds are expected. Be cautious when outdoors.")

    return recommendations, warnings

""" Modify the index_post function to integrate recommendations and warnings """
@app.route('/', methods=['GET', 'POST'])
def index_post():
    weather_data = None
    error = None
    recommendations = []
    warnings = []

    if request.method == 'POST':
        location = request.form['location']
        location = f"{location},{location}"
        try:
            weather_data = get_weather_data(location)
        except Exception as e:
            error = f"An error occurred while fetching weather data: {e}"
        else:
            if weather_data:
                recommendations, warnings = generate_recommendations_and_warnings(weather_data)
            else:
                error = "Location not found. Please try again."

    return render_template('index.html', weather_data=weather_data, error=error, recommendations=recommendations, warnings=warnings, current_time=datetime.datetime.now())

def get_weather_data(location):

    """
    Fetches weather data from WeatherAPI for the specified location.

    Args:
        location (str): The location for which weather data is to be fetched.

    Returns:
        dict: A dictionary containing weather information.
    """
    base_url = "http://api.weatherapi.com/v1/forecast.json"
    complete_url = f"{base_url}?key={WEATHER_API_KEY}&q={location}&days=5&aqi=no&alerts=no"  # Fetching 5 days forecast
    response = requests.get(complete_url)
    data = response.json()

    if 'error' not in data:
        current = data['current']
        forecast_days = data['forecast']['forecastday']

        """ Fetch hourly forecast for the current day starting from the current hour """
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        current_hour = datetime.datetime.now().hour
        hourly_forecast = []
        for forecast in forecast_days:
            if forecast['date'] == current_date:
                hourly_forecast = forecast['hour'][current_hour:]
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

if __name__ == '__main__':
    app.run(debug=True)
