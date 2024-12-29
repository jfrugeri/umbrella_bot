from __future__ import print_function
from sib_api_v3_sdk import Configuration, ApiClient, TransactionalEmailsApi, SendSmtpEmail
from sib_api_v3_sdk.rest import ApiException
from dotenv import load_dotenv
from colorama import Fore, Style
import os, json, textwrap

current_dir = os.path.dirname(__file__)
output_html_path = os.path.join("html_content", "generated_html.html")
html_content_dir = os.path.join(current_dir, '..', '..', 'html_content')
html_content_body = os.path.join(html_content_dir, "generated_html.html")
already_sent_path = os.path.join(current_dir, '..', '..', 'json_data', 'already_sent.json')

def mount_html_content(data):

    # Se o parâmetro for uma string, tenta tratar como um caminho para arquivo JSON
    if isinstance(data, str) and os.path.exists(data):
        with open(data) as file:
            days_data = json.load(file)
    elif isinstance(data, list):  # Se for uma lista, usa diretamente
        days_data = data
    else:
        print(f"\n - O parâmetro passado não é um arquivo válido ou uma lista de objetos.")
        return

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

    os.makedirs("html_content", exist_ok=True)

    with open(output_html_path, 'w', encoding='utf-8') as html_file:
        html_file.write(html_content)

    print(f"\n - HTML gerado com sucesso em '{output_html_path}'!\n")

def send_email(data):

    load_dotenv()
    configuration = Configuration()
    configuration.api_key['api-key'] = os.getenv('BREVO_API_KEY')
    from_email = os.getenv('FROM_EMAIL').strip()
    from_name = os.getenv('FROM_NAME').strip()
    to_email = os.getenv('TO_EMAIL').strip()
    to_name = os.getenv('TO_NAME').strip()

    # Carrega o conteudo html para ser usado no corpo do email
    with open(html_content_body, "r", encoding="utf-8") as file:
        html_content = file.read()

    api_instance = TransactionalEmailsApi(ApiClient(configuration))
    bcc = [] # Apenas habilitar se for necessário e passar no send_smtp_email como parâmetro
    cc = [] # Apenas habilitar se for necessário e passar no send_smtp_email como parâmetro
    headers = {}
    subject = "Alerta de chuva para os próximos dias"
    sender = {"name": from_name,"email": from_email}
    # replyTo = {"name":"Sendinblue","email":"contact@sendinblue.com"} # -> apenas habilitar se for necessário e passar no send_smtp_email como parâmetro
    html_content = html_content
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
    print(f"{Fore.LIGHTGREEN_EX}Email enviado com sucesso!\n{Style.RESET_ALL}")
    


    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        print(api_response)

        if os.path.exists(already_sent_path):

            # Atualizacao do already_sent.json com o data
            with open(already_sent_path, "r", encoding="utf-8") as file:
                already_sent = json.load(file)

            already_sent.extend(data)

            with open(already_sent_path, "w", encoding="utf-8") as file:
                json.dump(already_sent, file, indent=4)
            print ("arquivo already_sent.json atualizado com sucesso")
        
        else:
            # Cria um arquivo already_sent.json para armazenar os dias que já foram enviados
            with open(already_sent_path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4)
            print ("Primeira criacao do arquivo already_sent.json executada com sucesso")

        # Cria um arquivo alredy_sent.json para armazenar os dias que já foram enviados
        print(f"{Fore.LIGHTGREEN_EX}Email enviado com sucesso!{Style.RESET_ALL}")

    except ApiException as e:
        print(f"{Fore.LIGHTRED_EX}Exception when calling SMTPApi->send_transac_email: %s{Style.RESET_ALL}\n" % e)
    