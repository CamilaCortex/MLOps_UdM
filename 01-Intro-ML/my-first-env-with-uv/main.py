# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "requests",
# ]
# ///

import requests

def fetch_random_joke():
    """Fetch a random joke from an online API and return it as a string.""" 
    
    try:
        # Send a GET request to the joke API
        response = requests.get("https://official-joke-api.appspot.com/random_joke")
        response.raise_for_status()  # Raise an error if the response status is not 200
        joke_data = response.json()  # Parse the JSON response into a Python dict
        
        # Format the joke as "Setup - Punchline"
        return f"{joke_data['setup']} - {joke_data['punchline']}"
    except Exception as e:
        # In case of network issues or JSON parsing error, return an error message
        return f"Error fetching joke: {e}"

# Only execute this part when the script is run directly (not imported)
if __name__ == "__main__":
    print("Fetching a random joke from the internet...")
    joke = fetch_random_joke()
    print("Random Joke:", joke)