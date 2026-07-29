import pandas as pd
from pathlib import Path
from scripts.logger import obter_logger
from database import get_connection_db

logger = obter_logger(__name__)


def excel_to_sql(nome_excel, nome_tabela):
    caminho_excel = Path(__file__).parent.parent / "data" / nome_excel

    if not caminho_excel.exists():
        logger.warning(
            f"Excel não encontrado: {caminho_excel}. Pulando '{nome_tabela}'."
        )
        return

    df = pd.read_excel(caminho_excel)
    logger.info(f"Iniciando inserção de {nome_excel} na tabela '{nome_tabela}")

    if "Game_ID" in df.columns:
        df = df.rename(columns={"Game_ID": "game_id"})

    df.index = range(1, len(df) + 1)

    try:
        df.to_sql(
            name=nome_tabela,
            con=get_connection_db(),
            if_exists="replace",
            index=True,
            index_label="id",
        )
        logger.info(
            f"Tabela '{nome_tabela}' atualizada com sucesso ({len(df)} registros)."
        )
    except Exception as e:
        logger.warning(f"Erro ao inserir dados em '{nome_tabela}': {e}")


def games_to_sql():
    excel_to_sql("jogos_excel.xlsx", "jogos_brutos")


def main():
    games_to_sql()


if __name__ == "__main__":
    main()
