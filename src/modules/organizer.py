import time
import json
import os

# Definindo os diretórios
current_dir = os.path.dirname(os.path.abspath(__file__))
json_data_dir = os.path.join(current_dir, '..', '..', 'json_data')

def group_by_date():

    file_path_openweather_data = os.path.join(json_data_dir, "openweather_data.json")
    with open(file_path_openweather_data) as file:
        openweather_data = json.load(file)

    """
    O objetivo deste script e filtrar e agrupar os eventos de previsao do tempo por dia.
    Cada evento do weather_date tem uma data que as vezes se repete e as vezes nao.
    Houve entao a necessidade de agrupar os eventos por data, para que cada data tenha 
    todos os seus eventos(daily forecast) do mesmo dia.
    """

    # Filtragem e remontagem dos 5 dias com apenas dados necessários.
    def rebuild_daily_forecast(openweather_data):
        
        daily_forecast = []

        for object_item in openweather_data.get("list", []):
            
            group_by_daily_forecast_event = {}
            
            dt = object_item.get("dt")
            group_by_daily_forecast_event["date"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(dt)) if dt else None

            # Coleta das temperaturas
            main = object_item.get("main", {})
            group_by_daily_forecast_event["temp"] = main.get("temp")
            group_by_daily_forecast_event["min_temp"] = main.get("temp_min")
            group_by_daily_forecast_event["max_temp"] = main.get("temp_max")

            # Coleta das informações do clima
            weather = object_item.get("weather", [{}])
            group_by_daily_forecast_event["weather_main"] = weather[0].get("main", None)
            group_by_daily_forecast_event["weather_description"] = weather[0].get("description", None)

            # Coleta a precipitação de chuva
            pop = object_item.get("pop")
            group_by_daily_forecast_event["pop"] = pop

            daily_forecast.append(group_by_daily_forecast_event)

        return daily_forecast

    # Agrupamento dos eventos por data
    def group_by_date(daily_forecast):

        grouped_forecasts = {}

        # Separando data e hora dos eventos
        for event in daily_forecast:
            full_date = event["date"]
            if full_date:
                date, time = full_date.split(" ")
            else:
                continue

            # Passando a data e cada Daily forecast para o Objeto que e o dia do conjunto de eventos
            if date not in grouped_forecasts:
                grouped_forecasts[date] = {
                    "date": date,
                    "events": [],
                    "average_temp": 0,
                    "average_pop": 0
                }

            # Ajusta a key "date" para "time" no eventom daily forecast
            event_adjusted = event.copy()
            event_adjusted["time"] = time
            del event_adjusted["date"]

            grouped_forecasts[date]["events"].append(event_adjusted)

        # Calcula average_temp e average_pop para cada data
        for date, data in grouped_forecasts.items():
            total_temp = sum(event["temp"] for event in data["events"] if event["temp"] is not None)
            total_pop = sum(event["pop"] for event in data["events"] if event["pop"] is not None)
            count_temp = sum(1 for event in data["events"] if event["temp"] is not None)
            count_pop = sum(1 for event in data["events"] if event["pop"] is not None)
            
            data["average_temp"] = round((total_temp / count_temp if count_temp > 0 else None), 2)
            data["average_pop"] = round((total_pop / count_pop if count_pop > 0 else None), 2)

        return list(grouped_forecasts.values())

    # Criacao do dia da semana e agrupamento por datas
    daily_forecast = rebuild_daily_forecast(openweather_data) # <- recria os daily forecast de acordo com os dados necessarios
    grouped_daily_forecast = group_by_date(daily_forecast) # <- agrupa as daily em um unico dia - montando 5 dias de previsao

    file_patch_grouped_daily_forecast = os.path.join(json_data_dir, "grouped_daily_forecast.json")
    with open(file_patch_grouped_daily_forecast, 'w') as file:
        json.dump(grouped_daily_forecast, file, indent=4)

    print("\n - Dados agrupados com sucesso!\n")
    