from contextlib import contextmanager
import os, json, psycopg2

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

def check_if_rain():
    # Carrega dados agrupados da previsão semanal
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT grouped_daily_forecast FROM weather_data")
        result = cursor.fetchone()  # Retorna a primeira linha ou None
        cursor.close()

    # Garante que grouped_week seja uma lista vazia se result for None ou JSON inválido
    grouped_week = []
    if result and result[0]:
        try:
            grouped_week = json.loads(result[0]) if isinstance(result[0], str) else result[0]  # Tenta carregar os dados existentes
        except json.JSONDecodeError as e:
            print(f"Erro ao carregar grouped_daily_forecast: {e}")

    # Filtra os dias com probabilidade de chuva
    rainy_days = [days for days in grouped_week if days.get('average_pop', 0) > 0.13]

    # Atualiza ou insere os dias chuvosos no banco de dados
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Verifica se existe algum dado na coluna rainy_days para o id = 1
        cursor.execute("SELECT rainy_days FROM weather_data WHERE id = %s", (1,))
        result = cursor.fetchone()

        try:
            cursor.execute("""
                UPDATE weather_data
                SET rainy_days = %s
                WHERE id = %s
            """, (json.dumps(rainy_days), 1))
            print("\n - Dados de dias de chuva atualizados com sucesso!\n")
        except Exception as e:
            print(f"Erro ao atualizar rainy_days: {e}")
        finally:
            conn.commit()  # Salva as alterações
            cursor.close()

    print(f"Total de dias de chuva: {len(rainy_days)}")
    for day in rainy_days:
        print(f"- Data: {day['date']} - Precipitação: {day['average_pop']}")
    return

def already_sent():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT rainy_days FROM weather_data WHERE id = %s", (1,))
        rainy_days_result = cursor.fetchone()

        # Garante que rainy_days seja uma lista vazia se rainy_days_result for None ou JSON inválido
        if rainy_days_result and rainy_days_result[0]:
            try:
                rainy_days = json.loads(rainy_days_result[0]) if isinstance(rainy_days_result[0], str) else rainy_days_result[0]  # Tenta carregar os dados existentes
            except json.JSONDecodeError as e:
                print(f"Erro ao carregar dados da coluna rainy_days: {e}")
        
        cursor.execute("SELECT already_sent FROM weather_data WHERE id = %s", (1,))
        already_sent_result = cursor.fetchone()
        
        if already_sent_result and already_sent_result[0] not in [None, "null", "[null]"]:
            # Garante que already_sent seja uma lista válida
            try:
                already_sent = json.loads(already_sent_result[0]) if isinstance(already_sent_result[0], str) else already_sent_result[0]
            except json.JSONDecodeError as e:
                print(f"Erro ao carregar dados da coluna already_sent: {e}")
                already_sent = []
            
            diff_days = []

            for rainy_day in rainy_days:
                date = rainy_day.get("date")
                average_pop = rainy_day.get("average_pop")

                # Verifica se a data já está em already_sent e se houve mudança em "average_pop".
                sent_day = next((day for day in already_sent if day.get("date") == date), None)
                
                if not sent_day or (sent_day and average_pop >= 0.13 and sent_day.get("average_pop") != average_pop):
                    diff_days.append(rainy_day)

            # Se houver mudanças, prepara diff_days para envio
            if diff_days:
                print("Passando a lista de diff_days para montagem do conteúdo HTML...")
                data = diff_days
            else:
                print("Não há dias de chuva previstos.")
                data = False
        else:
            # Caso already_sent_result seja None, "null" ou "[null]"
            print("Passando a lista de rainy_days para montagem do conteúdo HTML...")
            data = rainy_days

    return data