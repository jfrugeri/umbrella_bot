from colorama import Fore, Style
import sys
import os
from src.modules import openweather, organizer, checker, email_alert

def main():
    print(f"\n{Fore.LIGHTCYAN_EX}------- OPENWEATHER DATA COLLECTION -------{Style.RESET_ALL}")
    openweather.get_weather_data()

    print(f"\n{Fore.LIGHTCYAN_EX}------- ORGANIZING FORECASTS -------{Style.RESET_ALL}")
    organizer.group_by_date()

    print(f"\n{Fore.LIGHTCYAN_EX}------- CHECKING FOR RAINY DAYS -------{Style.RESET_ALL}\n")
    checker.check_if_rain()

    print(f"\n{Fore.LIGHTCYAN_EX}------- CHECKING FOR ALREADY SENT DAYS -------{Style.RESET_ALL}\n")
    data = checker.already_sent()

    if data:
        print(f"\n{Fore.LIGHTCYAN_EX}------- MOUNTING EMAIL HTML -------{Style.RESET_ALL}\n")
        email_alert.mount_html_content(data)

        print(f"\n{Fore.LIGHTCYAN_EX}------- SENDING EMAIL ALERT -------{Style.RESET_ALL}\n")
        email_alert.send_email(data)
    else:
        print(f"{Fore.LIGHTYELLOW_EX}No alerts to be sent{Style.RESET_ALL}")

    print(f"\n{Fore.LIGHTYELLOW_EX}------- END  -------{Style.RESET_ALL}\n")

if __name__ == "__main__":
    main()