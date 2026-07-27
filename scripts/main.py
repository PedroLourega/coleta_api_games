# IMPORTS
import pandas as pd
import dagster as dg

PASTA_DESTINO = "../data/Relatorio_Games.xlsx"

def ler_dados_xlsx():
   df = pd.read_excel( PASTA_DESTINO)
   

def main():
 ...

if __name__ == "__main__":
    main()
