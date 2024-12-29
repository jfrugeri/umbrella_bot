import json
import os
from email_alert import mount_html_content

# Definicao de diretorios
current_dir = os.path.dirname(os.path.abspath(__file__))
json_data_dir = os.path.join(current_dir, '..', '..', 'json_data')
path_file_grouped_daily_foreast = os.path.join(json_data_dir, "grouped_daily_forecast.json")
file_path_rainy_days = os.path.join(json_data_dir, "rainy_days.json")
rainy_days_path = os.path.join(json_data_dir, "rainy_days.json")
already_sent_path = os.path.join(json_data_dir, "already_sent.json")

def check_if_rain():
    with open (path_file_grouped_daily_foreast) as file:
        grouped_week = json.load(file)

    rainy_days = []
    for days in grouped_week:
        if days['average_pop'] > 0.13: # Condicional de verificar se ira chover ou nao
            rainy_days.append(days)

    with open(file_path_rainy_days, 'w') as file:
        json.dump(rainy_days, file, indent=4)

    print(f"Total de dias de chuva: {len(rainy_days)}")
    for day in rainy_days:
        print(f"- Data: {day['date']} - Precipitação: {day['average_pop']}")
    
    return

def already_sent():
    if not os.path.exists(rainy_days_path):
        print(f"O arquivo ('{rainy_days_path}') não foi encontrado.")
        return None  # Retorna explicitamente None para indicar erro

    with open(rainy_days_path, 'r') as rainy_file:
        rainy_days = json.load(rainy_file)

    if os.path.exists(already_sent_path):
        with open(already_sent_path, 'r') as sent_file:
            already_sent = json.load(sent_file)

        diff_days = []

        for rainy_day in rainy_days:
            date = rainy_day.get("date")
            average_pop = rainy_day.get("average_pop")

            # Verifica se a data já está em (already_sent) e se houve mudança em "avarage_pop".
            sent_day = next((day for day in already_sent if day.get("date") == date), None)
            
            if not sent_day or (sent_day and average_pop >= 0.13 and sent_day.get("average_pop") != average_pop):
                diff_days.append(rainy_day)

        # Se houver mudanças, prepara diff_days para envio
        if diff_days:
            print("Passando a lista de diff_days para montagem do conteúdo HTML...")
            data = diff_days
        else:
            print("Nao ha dias de chuva previstos.")
            data = False
    else:
        # Caso o arquivo already_sent.json não exista, utiliza todos os dias de chuva
        print("Passando a lista de rainy_days para montagem do conteúdo HTML...")
        data = rainy_days

    return data


