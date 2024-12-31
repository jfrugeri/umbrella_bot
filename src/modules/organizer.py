import time, json, os, psycopg2
from contextlib import contextmanager

@contextmanager
def get_db_connection():
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )
    try:
        yield conn
    finally:
        conn.close()

def group_by_date():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT openweather_data FROM weather_data")
        result = cursor.fetchone()
        openweather_data = result[0] if result else {}
        cursor.close()

    def rebuild_daily_forecast(openweather_data):
        daily_forecast = []
        for object_item in openweather_data.get("list", []):
            group_by_daily_forecast_event = {}
            dt = object_item.get("dt")
            group_by_daily_forecast_event["date"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(dt)) if dt else None
            main = object_item.get("main", {})
            group_by_daily_forecast_event["temp"] = main.get("temp")
            group_by_daily_forecast_event["min_temp"] = main.get("temp_min")
            group_by_daily_forecast_event["max_temp"] = main.get("temp_max")
            weather = object_item.get("weather", [{}])
            group_by_daily_forecast_event["weather_main"] = weather[0].get("main", None)
            group_by_daily_forecast_event["weather_description"] = weather[0].get("description", None)
            pop = object_item.get("pop")
            group_by_daily_forecast_event["pop"] = pop
            daily_forecast.append(group_by_daily_forecast_event)
        return daily_forecast

    def group_by_date(daily_forecast):
        grouped_forecasts = {}
        for event in daily_forecast:
            full_date = event["date"]
            if full_date:
                date, time = full_date.split(" ")
            else:
                continue
            if date not in grouped_forecasts:
                grouped_forecasts[date] = {
                    "date": date,
                    "events": [],
                    "average_temp": 0,
                    "average_pop": 0
                }
            event_adjusted = event.copy()
            event_adjusted["time"] = time
            del event_adjusted["date"]
            grouped_forecasts[date]["events"].append(event_adjusted)
            
        for date, data in grouped_forecasts.items():
            total_temp = sum(event["temp"] for event in data["events"] if event["temp"] is not None)
            total_pop = sum(event["pop"] for event in data["events"] if event["pop"] is not None)
            count_temp = sum(1 for event in data["events"] if event["temp"] is not None)
            count_pop = sum(1 for event in data["events"] if event["pop"] is not None)
            data["average_temp"] = round((total_temp / count_temp if count_temp > 0 else None), 2)
            data["average_pop"] = round((total_pop / count_pop if count_pop > 0 else None), 2)
        return list(grouped_forecasts.values())

    daily_forecast = rebuild_daily_forecast(openweather_data)
    grouped_daily_forecast = group_by_date(daily_forecast)

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Verifica se existe conteúdo na coluna grouped_daily_forecast onde id = 1
        cursor.execute("""
            SELECT grouped_daily_forecast
            FROM weather_data
            WHERE id = %s
        """, (1,))
        result = cursor.fetchone()

        if result:  # Existe registro com id = 1
            cursor.execute("""
                UPDATE weather_data
                SET grouped_daily_forecast = %s
                WHERE id = %s
            """, (json.dumps(grouped_daily_forecast), 1))
            print("\n - Dados agrupados atualizados com sucesso!\n")
        else: 
            cursor.execute("""
                INSERT INTO weather_data (id, grouped_daily_forecast)
                VALUES (%s, %s)
            """, (1, json.dumps(grouped_daily_forecast)))
            print("- Dados agrupados inseridos com sucesso!\n")
            
        conn.commit()
        cursor.close()

    print("- Dados agrupados com sucesso!\n")