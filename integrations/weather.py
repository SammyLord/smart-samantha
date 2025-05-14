import requests

GEOCODING_API_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"

def get_weather_data(location: str) -> str:
    """Placeholder for fetching weather data."""
    if not location:
        return "I can get the weather for you, but I need a location!"

    try:
        # 1. Geocode location to latitude/longitude
        geo_params = {"name": location, "count": 1, "language": "en", "format": "json"}
        geo_response = requests.get(GEOCODING_API_URL, params=geo_params)
        geo_response.raise_for_status()
        geo_data = geo_response.json()

        if not geo_data.get("results"):
            return f"Sorry, I couldn't find geographic coordinates for '{location}'."

        lat = geo_data["results"][0]["latitude"]
        lon = geo_data["results"][0]["longitude"]
        display_name = geo_data["results"][0].get("name", location)
        country = geo_data["results"][0].get("country", "")
        admin1 = geo_data["results"][0].get("admin1", "")
        full_loc_name = f"{display_name}{f', {admin1}' if admin1 and admin1 != display_name else ''}{f', {country}' if country else ''}"

        # 2. Get weather for the coordinates
        weather_params = {
            "latitude": lat,
            "longitude": lon,
            "current_weather": "true",
            "temperature_unit": "celsius", # Or fahrenheit
            "windspeed_unit": "kmh",
            "precipitation_unit": "mm",
            "timezone": "auto"
        }
        weather_response = requests.get(WEATHER_API_URL, params=weather_params)
        weather_response.raise_for_status()
        weather_data = weather_response.json()

        current = weather_data.get("current_weather")
        if not current:
            return f"Sorry, I found '{full_loc_name}' but couldn't get current weather data for it."

        temp = current.get("temperature")
        windspeed = current.get("windspeed")
        weather_code = current.get("weathercode")
        # You can add a mapping for weather_code to description
        # (e.g., 0: Clear sky, 1: Mainly clear, etc. - See Open-Meteo docs)
        weather_desc = get_weather_description(weather_code)
        
        return f"The current weather in {full_loc_name} is: {weather_desc}, Temperature: {temp}°C, Windspeed: {windspeed} km/h."

    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data for {location}: {e}")
        return f"Sorry, I'm having trouble fetching the weather for {location} right now."
    except (KeyError, IndexError) as e:
        print(f"Error parsing weather data for {location}: {e}")
        return f"Sorry, there was an issue processing the weather information for {location}."

def get_weather_description(code: int) -> str:
    # WMO Weather interpretation codes (simplified)
    # Full list: https://open-meteo.com/en/docs#weathervariables
    descriptions = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        56: "Light freezing drizzle",
        57: "Dense freezing drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        66: "Light freezing rain",
        67: "Heavy freezing rain",
        71: "Slight snow fall",
        73: "Moderate snow fall",
        75: "Heavy snow fall",
        77: "Snow grains",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        85: "Slight snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm", # Slight or moderate
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail"
    }
    return descriptions.get(code, "Unknown weather condition") 