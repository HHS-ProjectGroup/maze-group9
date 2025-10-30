import os
import requests
import json
import random

# Expanded list of locations: [city, state/region, country]
# Use exact names as expected by IQAir API.
LOCATIONS_LIST = [
    ["Berlin", "Berlin", "Germany"],
    ["Munich", "Bavaria", "Germany"],
    ["Hamburg", "Hamburg", "Germany"],
    ["Frankfurt am Main", "Hesse", "Germany"],
    ["Cologne", "North Rhine-Westphalia", "Germany"],
    ["Rotterdam", "South Holland", "Netherlands"],
    ["The Hague", "South Holland", "Netherlands"],
    ["Amsterdam", "North Holland", "Netherlands"],
    ["Maastricht", "Limburg", "Netherlands"],
    ["Utrecht", "Utrecht", "Netherlands"],
    ["Eindhoven", "North Brabant", "Netherlands"],
    ["Groningen", "Groningen", "Netherlands"],
    ["Paris", "Ile-de-France", "France"],
    ["Lyon", "Auvergne-Rhone-Alpes", "France"],
    ["Marseille", "Provence-Alpes-Cote d'Azur", "France"],
    ["London", "England", "United Kingdom"],
    ["Manchester", "England", "United Kingdom"],
    ["Birmingham", "England", "United Kingdom"],
    ["New York", "New York", "USA"],
    ["Los Angeles", "California", "USA"],
    ["San Francisco", "California", "USA"],
    ["Chicago", "Illinois", "USA"],
    ["Houston", "Texas", "USA"],
    ["Seattle", "Washington", "USA"],
    ["Phoenix", "Arizona", "USA"],
    ["Toronto", "Ontario", "Canada"],
    ["Vancouver", "British Columbia", "Canada"],
    ["Montreal", "Quebec", "Canada"],
    ["Delhi", "Delhi", "India"],
    ["Mumbai", "Maharashtra", "India"],
    ["Bengaluru", "Karnataka", "India"],
    ["Kolkata", "West Bengal", "India"],
    ["Beijing", "Beijing", "China"],
    ["Shanghai", "Shanghai", "China"],
    ["Shenzhen", "Guangdong", "China"],
    ["Guangzhou", "Guangdong", "China"],
    ["Tokyo", "Tokyo", "Japan"],
    ["Osaka", "Osaka", "Japan"],
    ["Sydney", "New South Wales", "Australia"],
    ["Melbourne", "Victoria", "Australia"],
    ["Mexico City", "Mexico City", "Mexico"],
    ["Guadalajara", "Jalisco", "Mexico"],
    ["Sao Paulo", "Sao Paulo", "Brazil"],
    ["Rio de Janeiro", "Rio de Janeiro", "Brazil"],
]


def get_current_aqi(city, state, country, api_key):
    """
    Fetches the current Air Quality Index (AQI-US) for a specified city.

    :param city: The name of the city (e.g., 'Los Angeles').
    :param state: The name of the state/region (e.g., 'California').
    :param country: The name of the country (e.g., 'USA').
    :param api_key: Your IQAir AirVisual API key.
    :return: The AQI value (integer) or None if an error occurs.
    """
    base_url = "http://api.airvisual.com/v2/city"

    params = {"city": city, "state": state, "country": country, "key": api_key}

    print(f"Fetching AQI for {city}, {state}, {country}...")

    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("status") == "success":
            aqi_us = data["data"]["current"]["pollution"]["aqius"]
            return aqi_us
        else:
            error_message = data.get("data", {}).get("message", "Unknown API Error")
            print(f"API failed to fetch data. Error: {error_message}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error connecting to the API: {e}")
        return None
    except KeyError:
        print("Error: Could not find the AQI in the response data structure.")
        return None
    except json.JSONDecodeError:
        print("Error: Could not decode the API response as JSON.")
        return None


def aqi_category(aqi):
    """Return a simple category name for an AQI value (US EPA scale)."""
    try:
        aqi = int(aqi)
    except Exception:
        return "Unknown"
    if aqi <= 50:
        return "Good"
    if aqi <= 100:
        return "Moderate"
    if aqi <= 150:
        return "Unhealthy for Sensitive Groups"
    if aqi <= 200:
        return "Unhealthy"
    if aqi <= 300:
        return "Very Unhealthy"
    return "Hazardous"


def prompt_int(prompt_text):
    """Prompt the user until they enter an integer. Returns the integer."""
    while True:
        s = input(prompt_text).strip()
        try:
            return int(s)
        except ValueError:
            print("Please enter a whole number (integer). Try again.")


def get_api_key(default_key: str) -> str:
    """Pick API key from env AIRVISUAL_API_KEY if available, otherwise use default."""
    env_key = os.environ.get("AIRVISUAL_API_KEY")
    if env_key:
        return env_key
    return default_key


# Its probably easier to call beat_game() directly from here
def aqi_challenge() -> int:
    # Default API key (can be overridden by env or user input below)
    YOUR_API_KEY = "7e862e84-ddbd-435d-b712-cea20a365aa3"

    print("Welcome to the AQI Lookup Challenge!")
    print(
        "I'll give you a random location. Your task: look up the CURRENT AQI (US) on the internet and enter it here."
    )
    print(
        "This is NOT a guessing game — please research the value first. Lower AQI is better (0-50 Good, 51-100 Moderate, 101-150 Unhealthy for Sensitive Groups, etc.)."
    )
    print(
        "You can play multiple rounds; we'll check your entry against the live IQAir API."
    )
    print("-")

    # Allow user to override API key quickly if needed
    key = get_api_key(YOUR_API_KEY)
    use_custom = input("Use a custom API key? (leave blank to use current) ").strip()
    if use_custom:
        key = use_custom

    correct = 0
    rounds_played = 0
    # Small tolerance to account for minute-by-minute changes between websites (e.g., ±3 AQI)
    TOLERANCE = 3

    while True:
        # Pick a random location and attempt to fetch AQI. Retry a few times if API fails.
        attempts = 0
        aqi = None
        chosen = None
        while attempts < 5 and aqi is None:
            chosen = random.choice(LOCATIONS_LIST)
            city, state, country = chosen
            aqi = get_current_aqi(city, state, country, key)
            attempts += 1
            if aqi is None:
                print("Couldn't get data for that location. Trying another...")

        if aqi is None:
            print("Sorry, the API isn't responding right now. Please try again later.")
            break

        print("-")
        print(f"Lookup the current AQI (US) for: {city}, {state}, {country}")
        print(
            "When you have the number, enter it below. If the source shows a range or non-integer, round to the nearest whole number."
        )
        entered = prompt_int("Enter the AQI you found: ")

        diff = abs(entered - aqi)
        rounds_played += 1

        is_correct = diff <= TOLERANCE
        if is_correct:
            correct += 1
            print("Correct (within tolerance)! ✅")
            return 0
        else:
            print("Not an exact match. ❌")

        print("-")
        print(f"Actual AQI in {city}: {aqi} ({aqi_category(aqi)})")
        print(f"Your entry: {entered} | Difference: {diff} | Tolerance: ±{TOLERANCE}")
        print("-")

        again = (
            input("Play another round? (y to continue, anything else to quit): ")
            .strip()
            .lower()
        )
        if again != "y":
            break

    accuracy = (correct / rounds_played * 100) if rounds_played else 0.0
    print("Thanks for playing!")
    print(
        f"Rounds played: {rounds_played} | Correct (within ±{TOLERANCE}): {correct} | Accuracy: {accuracy:.1f}%"
    )
    return 1


# --- Text-based AQI Lookup Challenge ---
if __name__ == "__main__":
    aqi_challenge()
