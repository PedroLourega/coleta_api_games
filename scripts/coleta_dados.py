import requests
import pandas as pd
import time
from pathlib import Path
from datetime import datetime
from .logger import obter_logger

logger = obter_logger(__name__)

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}


def _obter_lojas():
    url = "https://www.cheapshark.com/api/1.0/stores"

    try:
        resposta = requests.get(url, headers=HEADERS)
        if resposta.status_code == 200:
            dados = resposta.json()
            dados_coletados = {loja["storeID"]: loja["storeName"] for loja in dados}
            logger.info("Sucesso na importação das lojas.")
            return dados_coletados
    except Exception as e:
        logger.info(f"Falha na importação dos Dados da API...\nErro: {e}")

    return {}


def _montar_registro(item, lojas_map):
    data_lancamento = None

    if item.get("releaseDate") and int(item["releaseDate"]) > 0:
        data_lancamento = datetime.fromtimestamp(int(item["releaseDate"])).strftime(
            "%Y-%m-%d"
        )

    return {
        "Game_ID": item.get("gameID"),
        "Title": item.get("title"),
        "Store": lojas_map.get(item.get("storeID"), "Desconhecida"),
        "Normal_Price": float(item.get("normalPrice", 0)),
        "Sale_Price": float(item.get("salePrice", 0)),
        "Discount_Percent": float(item.get("savings", 0)),
        "Metacritic_Score": item.get("metacriticScore"),
        "Steam_Rating_Pct": item.get("steamRatingPercent"),
        "Release_Date": data_lancamento,
        "Thumb": item.get("thumb"),
    }


def _extrair_deals(paginas=100, apenas_promocao=False):
    lojas_map = _obter_lojas()
    lista_games = []
    tipo = "promoções" if apenas_promocao else "catálogo geral"

    logger.info(f"Iniciando extração de {paginas} páginas ({tipo})...")

    for pagina in range(paginas):
        url = "https://www.cheapshark.com/api/1.0/deals"
        params = {"pageNumber": pagina, "pageSize": 60}

        if apenas_promocao:
            params["onSale"] = 1
            params["sortBy"] = "Savings"
        else:
            params["sortBy"] = "Title"

        try:
            resposta = requests.get(url, params=params, headers=HEADERS)
            resposta.raise_for_status()

            dados_pagina = resposta.json()

            if not dados_pagina:
                logger.info(f"[{tipo}] Página {pagina} veio vazia, encerrando.")
                break

            for item in dados_pagina:
                lista_games.append(_montar_registro(item, lojas_map))

            logger.info(f"[{tipo}] Página {pagina} processada com sucesso.")
            time.sleep(1)

        except requests.exceptions.HTTPError as erro_http:
            logger.error(f"Erro HTTP na página {pagina} ({tipo}): {erro_http}")
            break
        except requests.exceptions.RequestException as erro_requests:
            logger.error(
                f"Erro na rede ou conexão do Requests ({tipo}): {erro_requests}"
            )
            break
        except Exception as e:
            logger.exception(f"Erro no sistema ({tipo}): {e}")
            break

    if lista_games:
        sem_desconto = sum(1 for g in lista_games if g["Discount_Percent"] == 0)
        logger.info(
            f"[{tipo}] Extração finalizada: {len(lista_games)} registros "
            f"({sem_desconto} sem desconto ativo, {len(lista_games) - sem_desconto} com desconto)."
        )
    else:
        logger.info(f"[{tipo}] Extração finalizada: 0 registros.")

    return lista_games


def _salvar_excel(dados, nome_arquivo):
    pasta_data = Path(__file__).resolve().parent.parent / "data"
    save_excel = pasta_data / nome_arquivo

    if save_excel.exists():
        save_excel.unlink()
        logger.info(f"Arquivo antigo '{nome_arquivo}' deletado.")

    if dados:
        df_games = pd.DataFrame(dados)
        df_games.to_excel(save_excel, index=False)
        logger.info(f"Arquivo gerado em: {save_excel} ({len(dados)} registros).")
    else:
        logger.info(f"Não foi possível gerar '{nome_arquivo}': nenhum dado coletado.")


def jogos_gerais_to_excel(paginas=100):
    dados = _extrair_deals(paginas=paginas, apenas_promocao=False)
    _salvar_excel(dados, "jogos_excel.xlsx")


def promocoes_to_excel(paginas=100):
    dados = _extrair_deals(paginas=paginas, apenas_promocao=True)
    _salvar_excel(dados, "jogos_promocoes_excel.xlsx")


def main():
    jogos_gerais_to_excel()
    promocoes_to_excel()


if __name__ == "__main__":
    main()
