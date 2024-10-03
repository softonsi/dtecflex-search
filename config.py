import os

from dotenv import find_dotenv, load_dotenv

load_dotenv()  # Carrega as variáveis do arquivo .env

DATABASE_URL = os.getenv('DATABASE_URL')

dotenv_path = find_dotenv()
if dotenv_path:
    load_dotenv(dotenv_path)
    # logger.info(f'.env file found and loaded: {dotenv_path}')
    print(f'.env file found and loaded: {dotenv_path}')
else:
    #logger.error('.env file not found')
    print('.env file not found')


def build_connetion_url():
    dbuser = os.getenv('DB_USER')
    dbpass = os.getenv('DB_PASS')
    dbhost = os.getenv('DB_HOST')
    dbport = os.getenv('DB_PORT')
    dbname = os.getenv('DB_NAME')
    str_conn = f'mysql+pymysql://{dbuser}:{dbpass}@{dbhost}:{dbport}/{dbname}'
    return str_conn


DATABASE_URL = build_connetion_url()

print(DATABASE_URL)
