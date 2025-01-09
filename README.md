# Umbrella Bot

Umbrella Bot é um aplicativo Python que coleta dados meteorológicos, organiza previsões e envia alertas de chuva por e-mail. Este projeto utiliza diversas APIs e bibliotecas para fornecer informações precisas sobre o clima e garantir que você esteja sempre preparado para dias chuvosos.

## Funcionalidades

- Coleta de dados meteorológicos usando a API do OpenWeather.
- Organização das previsões do tempo por data.
- Verificação de dias com previsão de chuva.
- Envio de alertas por e-mail para dias chuvosos.

## Estrutura do Projeto

- `main.py`: Ponto de entrada principal do script. Executa as funções principais do aplicativo.
- `app.py`: Configura um servidor Flask para executar scripts remotamente via HTTP GET.
- `src/modules/checker.py`: Verifica previsões de chuva e atualiza os dados no banco de dados.
- `src/modules/email_alert.py`: Monta o conteúdo HTML dos e-mails e envia alertas.
- `src/modules/openweather.py`: Coleta dados meteorológicos usando a API do OpenWeather.
- `src/modules/organizer.py`: Organiza as previsões do tempo por data e calcula médias.

## Requisitos

- Python 3.x
- Bibliotecas: Flask, requests, psycopg2, dotenv, colorama, sib_api_v3_sdk

## Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/jfrugeri/umbrella_bot.git
   ```
2. Navegue até o diretório do projeto:
   ```bash
   cd umbrella_bot
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

## Configuração

1. Crie um arquivo `.env` na raiz do projeto e adicione as seguintes variáveis:
   ```
   OPENWEATHER_API_KEY=your_openweather_api_key
   GEOCODING_API_KEY=your_geocoding_api_key
   DB_NAME=your_database_name
   DB_USER=your_database_user
   DB_PASSWORD=your_database_password
   DB_HOST=your_database_host
   DB_PORT=your_database_port
   FROM_EMAIL=your_email
   FROM_NAME=your_name
   TO_EMAIL=recipient_email
   TO_NAME=recipient_name
   BREVO_API_KEY=your_brevo_api_key
   ALLOWED_IPS=comma_separated_allowed_ips
   CITY_NAME=your_city_name
   POSTAL_CODE=your_postal_code
   ```

## Uso

1. Para executar o script principal:
   ```bash
   python main.py
   ```
2. Para executar o servidor Flask:
   ```bash
   python app.py
   ```

## Contribuição

Se você quiser contribuir com este projeto, sinta-se à vontade para abrir um pull request ou relatar issues.

## Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

---
