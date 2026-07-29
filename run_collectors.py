# run_collectors.py
from scripts.coleta_dados import games_to_excel as coletar_cheapshark
from scripts.steam import games_to_excel as coletar_steam
from scripts.sobe_dados_db import main as subir_banco


def main():
    # coletar_cheapshark()
    # coletar_steam()
    subir_banco()


if __name__ == "__main__":
    main()
