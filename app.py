from flask import Flask, jsonify, render_template
from database import get_connection_db
import sqlite3
import pandas as pd
from sqlalchemy import create_engine
from pathlib import Path


app = Flask(__name__)


@app.route("/api/items", methods=["GET"])
def listar_items():
    conn = get_connection_db()
    items = conn.execute("SELECT * FROM jogos_brutos").fetchall()
    conn.close()

    return jsonify([dict(ix) for ix in items])


def obter_melhores_promocoes(limite=6):
    caminho_db = Path(__file__).parent.parent / "databases" / "db.sqlite3"
    engine = create_engine(f"sqlite:///{caminho_db.as_posix()}")

    df_cheapshark = pd.read_sql("SELECT * FROM jogos_brutos", engine)
    df_steam = pd.read_sql("SELECT * FROM promocoes_steam", engine)

    df = pd.concat([df_cheapshark, df_steam], ignore_index=True)
    df = df.sort_values("Discount_Percent", ascending=False).head(limite)

    return df.to_dict(orient="records")


@app.route("/")
def home():
    # promocoes = obter_melhores_promocoes()
    return render_template("homepage.html")


if __name__ == "__main__":
    app.run(debug=True)
