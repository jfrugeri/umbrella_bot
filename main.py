from  colorama import Fore, Style
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "src/modules")))
from src.modules import openweather, organizer, checker, email_alert

if __name__ == "__main__":
    
    print(f"\n{Fore.LIGHTCYAN_EX}------- COLETA DO OPENWEATHER -------{Style.RESET_ALL}")
    openweather.get_weather_data()

    print(f"\n{Fore.LIGHTCYAN_EX}------- ORGANIZACAO DAS PREVISOES -------{Style.RESET_ALL}")
    organizer.group_by_date()

    print(f"\n{Fore.LIGHTCYAN_EX}------- CHECAGEM DE DIAS DE CHUVA -------{Style.RESET_ALL}\n")
    checker.check_if_rain()

    print(f"\n{Fore.LIGHTCYAN_EX}------- CHECAGEM DE DIAS JA ENVIADOS -------{Style.RESET_ALL}\n")
    data = checker.already_sent()

    if data:
        print(f"\n{Fore.LIGHTCYAN_EX}------- MONTANDO O HTML DO EMAIL -------{Style.RESET_ALL}\n")
        email_alert.mount_html_content(data)

        print(f"\n{Fore.LIGHTCYAN_EX}------- ENVIO DO ALERTA POR EMAIL -------{Style.RESET_ALL}\n")
        email_alert.send_email(data)
    else:
        print(f"{Fore.LIGHTYELLOW_EX}Nenhum alerta a ser enviado.{Style.RESET_ALL}")

    print(f"\n{Fore.LIGHTYELLOW_EX}------- FIM DO PROGRAMA -------{Style.RESET_ALL}\n")

# Incluir limpeza do already_sent.json pra nao ficar gigante
# Incluir a funcao de criar o arquivo de log