from sqlalchemy import create_engine
from urllib.parse import quote_plus
import os
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def _load_env():
    # Tenta /opt/airflow/config/.env (dentro do container) e depois fallback relativo
    for p in [Path('/opt/airflow/config/.env'), Path(__file__).resolve().parent.parent / 'config' / '.env']:
        if p.exists():
            load_dotenv(p, override=False)
            break

_load_env()

def _get_conn_params():
    return {
        'user': os.getenv('POSTGRES_USER'),
        'password': os.getenv('POSTGRES_PASSWORD'),
        'database': os.getenv('POSTGRES_DB'),
        'host': os.getenv('POSTGRES_HOST', 'postgres'),
    }

# Leitura lazy para suportar override via env do docker-compose
def get_engine():
    cfg = _get_conn_params()
    user = cfg['user']
    password = cfg['password']
    database = cfg['database']
    host = cfg['host']
    if not all([user, password, database, host]):
        logging.warning(f"Variaveis de conexao incompletas: user={user!r} host={host!r} db={database!r} pwd_set={bool(password)}")
    # quote_plus para caracteres especiais, client_encoding UTF8 evita 0xe7 (ç) latin1
    user_q = quote_plus(user) if user else ''
    pwd_q = quote_plus(password) if password else ''
    db_q = quote_plus(database) if database else ''
    url = f"postgresql+psycopg2://{user_q}:{pwd_q}@{host}:5432/{db_q}"
    safe_url = f"postgresql+psycopg2://{user_q}:***@{host}:5432/{db_q}"
    logging.info(f"->Conectando em {host}:5432/{database} (url={safe_url})")
    return create_engine(
        url,
        connect_args={"client_encoding": "utf8", "options": "-c client_encoding=utf8"},
        pool_pre_ping=True,
    )

def load_weather_data(table_name:str, df):
    engine = get_engine()
    try:
        df.to_sql(
            name=table_name,
            con=engine,
            if_exists='append',
            index=False
        )
        logging.info(f"Dados carregados com sucesso!")
    except UnicodeDecodeError as e:
        # Erro mascarado: servidor retornou mensagem latin1 (ç 0xe7) e psycopg2 tentou utf-8
        raw = e.args[0] if e.args else str(e)
        try:
            decoded = raw.encode('utf-8', 'surrogateescape').decode('latin1') if isinstance(raw, str) else bytes(raw).decode('latin1')
        except Exception:
            decoded = raw
        logging.error(f"UnicodeDecodeError ao conectar (possivel mensagem latin1 do postgres): {decoded!r} - erro original: {e}")
        # Tenta extrair mensagem real reconectando com fallback latin1 para diagnostico
        raise RuntimeError(f"Falha de conexao mascarada por encoding. Mensagem decodificada latin1: {decoded}") from e
    except Exception as e:
        logging.exception(f"Erro ao carregar dados em {table_name}: {e}")
        raise

    try:
        df_check = pd.read_sql(f'SELECT * FROM {table_name}', con=engine)
        logging.info(f"Total de registros na tabela: {len(df_check)}\n")
    except Exception as e:
        logging.warning(f"Insercao ok mas falha ao verificar contagem: {e}")
