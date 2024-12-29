import os
import sys
import requests
import json
from dotenv import load_dotenv

# Definindo diretorios
current_dir = os.path.dirname(os.path.abspath(__file__))

def get_weather_data():
    
    env_path = os.path.join(current_dir, '..', '..', '.env')
    load_dotenv(env_path)
    openweather_api_key = os.getenv("OPENWEATHER_API_KEY")
    geocoding_api_key = os.getenv("GEOCODING_API_KEY")
    city_name = os.getenv("CITY_NAME").strip()
    postal_code = os.getenv("POSTAL_CODE").strip()
    limit = 1

    if not openweather_api_key or not geocoding_api_key:
        print("\n API keys not found")
        sys.exit(1)

    # Faz a busca da latitude e longitude da cidade
    geocoding_response = requests.get(f"http://api.openweathermap.org/geo/1.0/direct?q={city_name},{postal_code}&limit={limit}&appid={geocoding_api_key}")
    if geocoding_response.status_code == 200:
        lat = geocoding_response.json()[0]["lat"]
        lon = geocoding_response.json()[0]["lon"]
        print(f"\n - Coletado latitude e longitude de {city_name}")
    else:
        print(f"\n - Erro ao coletar dados - Geocoding API retornou o status code: {geocoding_response.status_code}")
        sys.exit(1)

    # Faz a busca dos dados do clima da cidade
    openweather_response = requests.get(f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=metric&appid={openweather_api_key}")

    if openweather_response.status_code == 200:

        json_data_dir = os.path.join(current_dir, '..', '..', 'json_data')
        
        file_path_openweather_data = os.path.join(json_data_dir, "openweather_data.json")
        with open(file_path_openweather_data, "w") as file:
            json.dump(openweather_response.json(), file, indent=4)
            print("\n - Previsoes coletadas com sucesso!\n")
    else:
        print(f"\n - Erro ao coletar os dados - Weather API retornou o status code: {openweather_response.status_code}")
        sys.exit(1)
