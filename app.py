from flask import Flask, render_template, request
import requests
from dotenv import load_dotenv
import os
from datetime import datetime
import pytz
import logging

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/query', methods=['GET'])
def query():
    user_query = request.args.get('q').lower()
    response = "I'm sorry, I didn't understand that."

    logging.debug(f"Received query: {user_query}")

    if 'weather' in user_query:
        city = extract_city(user_query)
        if city:
            response = get_weather(city)
        else:
            response = "Please specify a city for the weather."
    elif 'news' in user_query:
        if 'details' in user_query:
            try:
                index = int(user_query.split()[-1])
                response = get_news_details(index)
            except ValueError:
                response = "Please specify a valid news index for details."
        else:
            response = get_news()
    elif 'joke' in user_query:
        response = get_joke()
    elif 'time' in user_query:
        if 'in' in user_query:
            city = extract_city(user_query)
            if city:
                response = get_time(city)
            else:
                response = "Please specify a city for the time."
        else:
            response = get_time()
    elif 'date' in user_query:
        if 'in' in user_query:
            city = extract_city(user_query)
            if city:
                response = get_date(city)
            else:
                response = "Please specify a city for the date."
        else:
            response = get_date()
    elif 'reminder' in user_query:
        reminder = user_query.replace('reminder', '').strip()
        response = add_reminder(reminder)
    elif 'reminders' in user_query:
        response = get_reminders()

    logging.debug(f"Response: {response}")
    return response

def extract_city(query):
    query = query.lower()
    if 'weather in' in query or 'time in' in query or 'date in' in query:
        start_index = query.index('in') + len('in')
        city = query[start_index:].strip()
        return city
    return None

def get_weather(city):
    logging.debug(f"Getting weather for city: {city}")
    # Use the OpenCage Geocoding API to get the latitude, longitude, and country of the city
    api_key = os.getenv('OPENCAGE_API_KEY')
    geocode_url = f'https://api.opencagedata.com/geocode/v1/json?q={city}&key={api_key}'
    try:
        geocode_response = requests.get(geocode_url)
        geocode_response.raise_for_status()
        geocode_data = geocode_response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error retrieving geolocation data: {e}")
        return f"Error retrieving geolocation data: {e}"
    except ValueError:
        logging.error("Error decoding geolocation data.")
        return "Error decoding geolocation data."

    if not geocode_data['results']:
        logging.error(f"Could not retrieve geolocation data for {city}.")
        return f"Could not retrieve geolocation data for {city}."
    
    lat = geocode_data['results'][0]['geometry']['lat']
    lon = geocode_data['results'][0]['geometry']['lng']
    country = geocode_data['results'][0]['components']['country']
    
    # Use the Open-Meteo API to get the weather data
    weather_url = f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true'
    try:
        weather_response = requests.get(weather_url)
        weather_response.raise_for_status()
        weather_data = weather_response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error retrieving weather data: {e}")
        return f"Error retrieving weather data: {e}"
    except ValueError:
        logging.error("Error decoding weather data.")
        return "Error decoding weather data."

    if 'current_weather' not in weather_data:
        logging.error(f"Could not retrieve weather data for {city}.")
        return f"Could not retrieve weather data for {city}."
    
    weather_code = weather_data['current_weather']['weathercode']
    temperature_celsius = weather_data['current_weather']['temperature']
    weather_description = get_weather_description(weather_code)
    
    # Determine the temperature unit based on the country
    if country in ['United States', 'Bahamas', 'Cayman Islands', 'Liberia', 'Palau']:
        temperature_fahrenheit = (temperature_celsius * 9/5) + 32
        return f'The weather in {city.strip()} is currently {weather_description} with a temperature of {temperature_fahrenheit:.1f} degrees Fahrenheit.'
    else:
        return f'The weather in {city.strip()} is currently {weather_description} with a temperature of {temperature_celsius:.1f} degrees Celsius.'

def get_weather_description(weather_code):
    weather_descriptions = {
        0: 'Clear sky',
        1: 'Mainly clear',
        2: 'Partly cloudy',
        3: 'Overcast',
        # Add more weather codes and descriptions as needed
    }
    return weather_descriptions.get(weather_code, 'Unknown weather')

def get_news():
    api_key = os.getenv('NEWS_API_KEY')
    news_url = f'https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}'
    try:
        news_response = requests.get(news_url)
        news_response.raise_for_status()
        news_data = news_response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error retrieving news data: {e}")
        return f"Error retrieving news data: {e}"
    except ValueError:
        logging.error("Error decoding news data.")
        return "Error decoding news data."

    if 'articles' not in news_data:
        logging.error("Could not retrieve news data.")
        return "Could not retrieve news data."

    top_articles = news_data['articles'][:5]
    news_summary = "Here are the top news headlines:\n"
    for i, article in enumerate(top_articles):
        title = article['title'].split(' - ')[0]
        news_summary += f"{i+1}. {title}\n"
    return news_summary

def get_news_details(index):
    api_key = os.getenv('NEWS_API_KEY')
    news_url = f'https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}'
    try:
        news_response = requests.get(news_url)
        news_response.raise_for_status()
        news_data = news_response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error retrieving news data: {e}")
        return f"Error retrieving news data: {e}"
    except ValueError:
        logging.error("Error decoding news data.")
        return "Error decoding news data."

    if 'articles' not in news_data:
        logging.error("Could not retrieve news data.")
        return "Could not retrieve news data."

    top_articles = news_data['articles'][:5]
    if index < 1 or index > len(top_articles):
        logging.error("Invalid news index.")
        return "Invalid news index."

    article = top_articles[index - 1]
    return f"Details for news {index}: {article['title']} - {article['description']}\nRead more at: {article['url']}"

def get_joke():
    joke_url = 'https://official-joke-api.appspot.com/random_joke'
    try:
        joke_response = requests.get(joke_url)
        joke_response.raise_for_status()
        joke_data = joke_response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error retrieving joke data: {e}")
        return f"Error retrieving joke data: {e}"
    except ValueError:
        logging.error("Error decoding joke data.")
        return "Error decoding joke data."

    return f"Here's a joke for you: {joke_data['setup']} - {joke_data['punchline']}"

def get_time(city=None):
    if city:
        # Use the OpenCage Geocoding API to get the timezone of the city
        api_key = os.getenv('OPENCAGE_API_KEY')
        geocode_url = f'https://api.opencagedata.com/geocode/v1/json?q={city}&key={api_key}'
        try:
            geocode_response = requests.get(geocode_url)
            geocode_response.raise_for_status()
            geocode_data = geocode_response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error retrieving geolocation data: {e}")
            return f"Error retrieving geolocation data: {e}"
        except ValueError:
            logging.error("Error decoding geolocation data.")
            return "Error decoding geolocation data."

        if not geocode_data['results']:
            logging.error(f"Could not retrieve geolocation data for {city}.")
            return f"Could not retrieve geolocation data for {city}."
        
        timezone = geocode_data['results'][0]['annotations']['timezone']['name']
        city_time = datetime.now(pytz.timezone(timezone))
        return f"The current time in {city} is {city_time.strftime('%I:%M %p')}."
    else:
        # Use a geolocation API to get the user's location based on their IP address
        ip_api_key = os.getenv('IP_API_KEY')
        ip_url = f'http://api.ipstack.com/check?access_key={ip_api_key}'
        try:
            ip_response = requests.get(ip_url)
            ip_response.raise_for_status()
            ip_data = ip_response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error retrieving IP geolocation data: {e}")
            return f"Error retrieving IP geolocation data: {e}"
        except ValueError:
            logging.error("Error decoding IP geolocation data.")
            return "Error decoding IP geolocation data."

        logging.debug(f"IP data: {ip_data}")

        city = ip_data.get('city', 'Unknown city')
        country = ip_data.get('country_name', 'Unknown country')
        timezone = ip_data.get('location', {}).get('time_zone', {}).get('id', 'UTC')
        city_time = datetime.now(pytz.timezone(timezone))
        return f"The current time in {city}, {country} is {city_time.strftime('%I:%M %p')}."

def get_date(city=None):
    if city:
        # Use the OpenCage Geocoding API to get the timezone of the city
        api_key = os.getenv('OPENCAGE_API_KEY')
        geocode_url = f'https://api.opencagedata.com/geocode/v1/json?q={city}&key={api_key}'
        try:
            geocode_response = requests.get(geocode_url)
            geocode_response.raise_for_status()
            geocode_data = geocode_response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error retrieving geolocation data: {e}")
            return f"Error retrieving geolocation data: {e}"
        except ValueError:
            logging.error("Error decoding geolocation data.")
            return "Error decoding geolocation data."

        if not geocode_data['results']:
            logging.error(f"Could not retrieve geolocation data for {city}.")
            return f"Could not retrieve geolocation data for {city}."
        
        timezone = geocode_data['results'][0]['annotations']['timezone']['name']
        city_date = datetime.now(pytz.timezone(timezone))
        return f"The current date in {city} is {city_date.strftime('%A, %B %d, %Y')}."
    else:
        # Use a geolocation API to get the user's location based on their IP address
        ip_api_key = os.getenv('IP_API_KEY')
        ip_url = f'http://api.ipstack.com/check?access_key={ip_api_key}'
        try:
            ip_response = requests.get(ip_url)
            ip_response.raise_for_status()
            ip_data = ip_response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error retrieving IP geolocation data: {e}")
            return f"Error retrieving IP geolocation data: {e}"
        except ValueError:
            logging.error("Error decoding IP geolocation data.")
            return "Error decoding IP geolocation data."

        logging.debug(f"IP data: {ip_data}")

        city = ip_data.get('city', 'Unknown city')
        country = ip_data.get('country_name', 'Unknown country')
        timezone = ip_data.get('location', {}).get('time_zone', {}).get('id', 'UTC')
        city_date = datetime.now(pytz.timezone(timezone))
        return f"The current date in {city}, {country} is {city_date.strftime('%A, %B %d, %Y')}."

reminders = []

def get_reminders():
    if not reminders:
        return "No reminders set."
    return "Here are your reminders:\n" + "\n".join(f"- {reminder}" for reminder in reminders)

def add_reminder(reminder):
    reminders.append(reminder)
    return f"Reminder added: {reminder}"

if __name__ == '__main__':
    app.run(debug=True)