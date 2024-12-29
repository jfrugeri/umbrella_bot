import time
import json
import os

def build_days_from_events():

    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_data_dir = os.path.join(current_dir, '..', '..', 'json_data')

    # Coletando os dados do arquivo weather_data.json
    file_path_openweather_data = os.path.join(json_data_dir, "openweather_data.json")
    with open(file_path_openweather_data) as file:
        openweather_data = json.load(file)

    '''
        O objetivo deste script e filtrar e agrupar os eventos de previsao do tempo por dia.
        Cada evento do weather_date tem uma data que as vezes se repete e as vezes nao.
        Houve entao a necessidade de agrupar os eventos por data, para que cada data tenha 
        todos os seus eventos(daily forecast) do mesmo dia.
    '''

    # Filtragem e remontagem dos 5 dias com apenas dados necessários.
    def filtering_data(openweather_data):
        
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

            data["average_temp"] = ("{:.2f}".format(total_temp / count_temp) if count_temp > 0 else "0.00")
            data["average_pop"] = ("{:.2f}".format(total_pop / count_pop) if count_pop > 0 else "0.00")

        return list(grouped_forecasts.values())

    # Filtragem e agrupamento dos eventos
    week = filtering_data(openweather_data)
    grouped_week = group_by_date(week)

    file_patch_grouped_week = os.path.join(json_data_dir, "grouped_week.json")
    with open(file_patch_grouped_week, 'w') as file:
        json.dump(grouped_week, file, indent=4)

    print("2 - Dados agrupados com sucesso!\n")

build_days_from_events()