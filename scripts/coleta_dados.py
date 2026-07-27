from numpy import save
import requests
import pandas as pd
import time
import logging
from pathlib import Path
from datetime import datetime
from logger import obter_logger

logger = obter_logger(__name__)

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

def _obter_lojas():
    url = 'https://www.cheapshark.com/api/1.0/stores'
    
    try:
        resposta = requests.get(url, headers=HEADERS)
        if resposta.status_code == 200:
            dados = resposta.json()
            dados_coletados = {loja['storeID']: loja['storeName'] for loja in dados}
            logger.info('Sucesso na importação das lojas.')
            return dados_coletados
    except Exception as e:
        logger.info(f'Falha na importação dos Dados da API...\nErro: {e}')
    
    return {}

def _extrair_games_cheapshark(paginas=100):
    lojas_map = _obter_lojas()
    lista_games = []

    logger.info(f'Iniciando extração de {paginas} páginas...')

    for pagina in range(paginas):
        url = 'https://www.cheapshark.com/api/1.0/deals'
        
        params = {
            'pageNumber': pagina,
            'pageSize': 60
        }

        try:
            resposta = requests.get(url, params=params, headers=HEADERS)
            resposta.raise_for_status()

            dados_pagina = resposta.json()

            if not dados_pagina:
                break

            for item in dados_pagina:
                data_lancamento = None
                
                if item.get('releaseDate') and int(item['releaseDate']) > 0:
                    data_lancamento = datetime.fromtimestamp(int(item['releaseDate'])).strftime('%Y-%m-%d')

                registros = {
                    "Game_ID": item.get('gameID'),
                    "Title": item.get('title'),
                    "Store": lojas_map.get(item.get('storeID'), "Desconhecida"),
                    "Normal_Price": float(item.get('normalPrice', 0)),
                    "Sale_Price": float(item.get('salePrice', 0)),
                    "Metacritic_Score": item.get('metacriticScore'),
                    "Steam_Rating_Pct": item.get('steamRatingPercent'),
                    "Release_Date": data_lancamento
                }
                lista_games.append(registros)

            logger.info(f'Página: {pagina} processada com sucesso.')

            time.sleep(1) 

        except requests.exceptions.HTTPError as erro_http:
            logger.error(f"Erro HTTP na página {pagina}: {erro_http}")
            break 
        except requests.exceptions.RequestException as erro_requests:
            logger.error(f"Erro na rede ou conexão do Requests: {erro_requests}")
            break
        except Exception as e:
            logger.exception(f"Erro no sistema: {e}")
            break
            
    return lista_games

def games_to_excel():
    pasta_data = Path(__file__).resolve().parent.parent / 'data'
    save_excel = pasta_data / 'jogos_excel.xlsx'
    
    dados = _extrair_games_cheapshark()
    
    if save_excel.exists():
        save_excel.unlink()
        logger.info('O arquivo antigo excel foi deletado.')

    if dados:
        df_games = pd.DataFrame(dados)
        df_games.to_excel(save_excel, index=False)
        logger.info(f"Pipeline finalizado. Arquivo gerado em: {save_excel}")
    else:
        logger.info("Não foi possível gerar o arquivo.")

def main():
    games_to_excel()

if __name__ == "__main__":
    main()
