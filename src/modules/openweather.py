import os, sys, requests, json, psycopg2
from dotenv import load_dotenv

# Definindo diretorio atual
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
        print("API keys not found\n")
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
        weather_data = openweather_response.json()
        print("- Previsões coletadas com sucesso!\n")

        # Conecta ao banco de dados PostgreSQL
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        cursor = conn.cursor()

        # Verifica se existe conteúdo na coluna openweather_data onde id = 1
        cursor.execute("""
            SELECT openweather_data
            FROM weather_data
            WHERE id = %s
        """, (1,))
        result = cursor.fetchone()

        if result:  # Existe registro com id = 1
            cursor.execute("""
                UPDATE weather_data
                SET openweather_data = %s
                WHERE id = %s
            """, (json.dumps(weather_data), 1))
            print("- Dados atualizados com sucesso!\n")
        else:  # Não existe registro com id = 1
            cursor.execute("""
                INSERT INTO weather_data (id, openweather_data)
                VALUES (%s, %s)
            """, (1, json.dumps(weather_data)))
            print("- Dados inseridos com sucesso!\n")
            
        conn.commit()
        cursor.close()
        conn.close()
    else:
        print(f"- Erro ao coletar os dados - Weather API retornou o status code: {openweather_response.status_code}")
        sys.exit(1)
