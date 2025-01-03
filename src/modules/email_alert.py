from __future__ import print_function
from sib_api_v3_sdk import Configuration, ApiClient, TransactionalEmailsApi, SendSmtpEmail
from sib_api_v3_sdk.rest import ApiException
from dotenv import load_dotenv
from colorama import Fore, Style
from contextlib import contextmanager
from psycopg2 import sql
import os, json, textwrap, psycopg2

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

def mount_html_content(data):
    
    if not isinstance(data, list):
        print(f"\n - O parâmetro passado não é uma lista de objetos.")
        return
    else:
        days_data = data

    # Montagem do conteúdo HTML
    html_content_body = "\n".join(
        f"            <p>Data: {day['date']}, Precipitação: {day['average_pop']} - CHOVERÁ</p>"
        for day in days_data
    )

    html_content = textwrap.dedent(f"""\
    <html>
        <body>
            <h1>Dias que irão chover:</h1>
{html_content_body}
        </body>
    </html>
    """)

    # Salva o conteúdo HTML no banco de dados
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Verifica se já existe conteúdo na coluna html_content da tabela weather_data
        cursor.execute("SELECT html_content FROM weather_data WHERE id = 1")
        result = cursor.fetchone()

        query = sql.SQL("""
        INSERT INTO weather_data (id, html_content)
        VALUES (1, %s)
        ON CONFLICT (id)
        DO UPDATE SET html_content = EXCLUDED.html_content
        """)

        try:
            cursor.execute(query, [html_content])
            print(f"\n - HTML atualizado ou inserido com sucesso na tabela weather_data!\n")
        except Exception as e:
            print(f"Erro ao atualizar html_content: {e}")
        finally:
            conn.commit()
            conn.close()

def send_email(data):
    load_dotenv()
    configuration = Configuration()
    configuration.api_key['api-key'] = os.getenv('BREVO_API_KEY')
    from_email = os.getenv('FROM_EMAIL').strip()
    from_name = os.getenv('FROM_NAME').strip()
    to_email = os.getenv('TO_EMAIL').strip()
    to_name = os.getenv('TO_NAME').strip()

    # Carrega o conteudo html para ser usado no corpo do email
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Pega o conteúdo HTML da coluna html_content da tabela weather_data
        cursor.execute("SELECT html_content FROM weather_data WHERE id = 1")
        result = cursor.fetchone()
        
        if result and result[0] not in [None, "null", "[null]"]:
            html_content_from_db = result[0]
        else:
            print(f"{Fore.LIGHTRED_EX}Nenhum conteúdo HTML encontrado na tabela weather_data.{Style.RESET_ALL}")
            return
        cursor.close()

    api_instance = TransactionalEmailsApi(ApiClient(configuration))
    bcc = [] # Apenas habilitar se for necessário e passar no send_smtp_email como parâmetro
    cc = [] # Apenas habilitar se for necessário e passar no send_smtp_email como parâmetro
    headers = {}
    subject = "Alerta de chuva para os próximos dias"
    sender = {"name": from_name,"email": from_email}
    # replyTo = {"name":"Sendinblue","email":"contact@sendinblue.com"} # -> apenas habilitar se for necessário e passar no send_smtp_email como parâmetro
    html_content = html_content_from_db
    to = [{"email": to_email,"name": to_name}]
    params = {"parameter":"My param value","subject":"New Subject"}

    # Envia o transactional email
    send_smtp_email = SendSmtpEmail(
        to=to,  
        html_content=html_content, 
        sender=sender, 
        subject=subject,
        params=params
        )

    print(f"{Fore.LIGHTYELLOW_EX}Enviando email...{Style.RESET_ALL}")

    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        print(api_response)
        print(f"{Fore.LIGHTGREEN_EX}Email enviado com sucesso!\n{Style.RESET_ALL}")

        # Atualiza already_sent com o data
        with get_db_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                UPDATE weather_data
                SET already_sent = %s
                WHERE id = %s
                """, (json.dumps(data), 1))
            except Exception as e:
                print(f"Erro ao atualizar already_sent: {e}")
            finally:
                conn.commit()
                cursor.close()

    except ApiException as e:
        print(f"{Fore.LIGHTRED_EX}Exception when calling SMTPApi->send_transac_email: %s{Style.RESET_ALL}\n" % e)
        print(f"{Fore.LIGHTRED_EX}Erro ao enviar email.{Style.RESET_ALL}")