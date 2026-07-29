import requests
import pandas as pd
import time
from pathlib import Path
from scripts.logger import obter_logger

logger = obter_logger(__name__)

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}


def _extrair_promocoes_steam(cc="BR", idioma="brazilian"):
    """
    Busca as promoções em destaque da Steam
    """
    url = "https://store.steampowered.com/api/featuredcategories"
    params = {"cc": cc, "l": idioma}

    try:
        resposta = requests.get(url, params=params, headers=HEADERS, timeout=15)
        resposta.raise_for_status()
        dados = resposta.json()
    except requests.exceptions.HTTPError as erro_http:
        logger.error(f"Erro HTTP ao consultar a Steam: {erro_http}")
        return []
    except requests.exceptions.RequestException as erro_requests:
        logger.error(f"Erro na rede ou conexão com a Steam: {erro_requests}")
        return []
    except Exception as e:
        logger.exception(f"Erro ao consultar a Steam: {e}")
        return []

    itens = dados.get("specials", {}).get("items", [])
    logger.info(f"{len(itens)} promoções encontradas na Steam.")

    lista_games = []
    for item in itens:
        preco_normal = item.get("original_price")
        preco_final = item.get("final_price")

        registros = {
            "Game_ID": item.get("id"),
            "Title": item.get("name"),
            "Store": "Steam",
            "Normal_Price": (preco_normal / 100) if preco_normal else None,
            "Sale_Price": (preco_final / 100) if preco_final else None,
            "Discount_Percent": float(item.get("discount_percent", 0)),
            "Metacritic_Score": None,
            "Steam_Rating_Pct": None,
            "Release_Date": None,
            "Thumb": item.get("header_image") or item.get("large_capsule_image"),
        }
        lista_games.append(registros)

    return lista_games


def _enriquecer_com_appdetails(lista_games, cc="BR", limite=None):
    url = "https://store.steampowered.com/api/appdetails"
    alvo = lista_games[:limite] if limite else lista_games

    for jogo in alvo:
        appid = jogo["Game_ID"]
        if not appid:
            continue

        try:
            resposta = requests.get(
                url,
                params={
                    "appids": appid,
                    "cc": cc,
                    "filters": "basic,metacritic,release_date",
                },
                headers=HEADERS,
                timeout=15,
            )
            resposta.raise_for_status()
            dados = resposta.json().get(str(appid), {})

            if dados.get("success"):
                info = dados["data"]
                jogo["Metacritic_Score"] = info.get("metacritic", {}).get("score")
                data_lanc = info.get("release_date", {})
                if data_lanc and not data_lanc.get("coming_soon"):
                    jogo["Release_Date"] = data_lanc.get("date")

            logger.info(f"Enriquecido appid {appid}.")

        except Exception as e:
            logger.warning(f"Falha ao enriquecer appid {appid}: {e}")

        time.sleep(1.5)

    return lista_games


def games_to_excel(enriquecer=False, limite_enriquecimento=20):
    pasta_data = Path(__file__).resolve().parent.parent / "data"
    save_excel = pasta_data / "jogos_steam_excel.xlsx"

    dados = _extrair_promocoes_steam()

    if enriquecer and dados:
        logger.info("Iniciando enriquecimento com appdetails (mais lento)...")
        dados = _enriquecer_com_appdetails(dados, limite=limite_enriquecimento)

    if save_excel.exists():
        save_excel.unlink()
        logger.info("O arquivo antigo de promoções Steam foi deletado.")

    if dados:
        df_games = pd.DataFrame(dados)
        df_games.to_excel(save_excel, index=False)
        logger.info(f"Pipeline da Steam finalizado. Arquivo gerado em: {save_excel}")
    else:
        logger.info("Não foi possível gerar o arquivo da Steam.")


def main():
    games_to_excel(enriquecer=False)


if __name__ == "__main__":
    main()
