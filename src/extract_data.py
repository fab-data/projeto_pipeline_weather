import requests
import json
import os
from dotenv import load_dotenv
from pathlib import Path
import logging as log

for _p in [Path('/opt/airflow/config/.env'), Path(__file__).resolve().parent.parent / 'config' / '.env']:
    if _p.exists():
        load_dotenv(_p, override=False)
        break

log.basicConfig(
    level=log.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# lat = '-16.665136'
# lon = '-49.286041'
api_key = os.getenv('API_KEY_WEATHER')

url = f'https://api.openweathermap.org/data/2.5/weather?q=GOIANIA,BR&units=metric&appid={api_key}'
# https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={key}


def extract_weather_data(url:str) -> list:
    response = requests.get(url)

    if response.status_code != 200:
        
        try:
            resposta = response.json()
            mensagem = resposta.get("message", "message não informada pela API")
        except requests.exceptions.JSONDecodeError:
            mensagem = response.text
            
        log.error(f"Erro na requisição: status_code={response.status_code} message={mensagem}")
        return []
        
    
    data = response.json()
    
    if not data:
        log.warning("Nenhum dado retornado")
        return []
    
    # Resolve path relativo ao projeto, funcionando host e container (/opt/airflow/data)
    for cand in [Path('/opt/airflow/data/weather_data.json'), Path(__file__).resolve().parent.parent / 'data' / 'weather_data.json', Path('data/weather_data.json')]:
        if cand.parent.exists() or cand.parent == Path('/opt/airflow/data'):
            output_path = cand
            break
    else:
        output_path = Path('data/weather_data.json')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        
    log.info(f"Arquivo salvo em {output_path}")
    return data

if __name__ == "__main__":
    print(extract_weather_data(url))