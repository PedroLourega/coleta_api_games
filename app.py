from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash

from database import get_connection_db, init_db

app = Flask(__name__)
app.config["SECRET_KEY"] = "troque-essa-chave-por-uma-secreta-de-verdade-em-producao"

GAMES_POR_PAGINA = 12

login_manager = LoginManager()
login_manager.login_view = "welcome"
login_manager.init_app(app)

init_db()


class Usuario(UserMixin):
    def __init__(self, row):
        self.id = str(row["id"])
        self.nome = row["nome"]
        self.email = row["email"]


@login_manager.user_loader
def load_user(user_id):
    conn = get_connection_db()
    row = conn.execute("SELECT * FROM usuarios WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return Usuario(row) if row else None


@app.route("/welcome")
def welcome():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    return render_template("welcome.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")

        conn = get_connection_db()
        row = conn.execute(
            "SELECT * FROM usuarios WHERE email = ?", (email,)
        ).fetchone()
        conn.close()

        if row and check_password_hash(row["senha_hash"], senha):
            login_user(Usuario(row))
            return redirect(url_for("home"))

        flash("Email ou senha inválidos.")

    return render_template("login.html")


@app.route("/registrar", methods=["GET", "POST"])
def registrar():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")

        if not nome or not email or len(senha) < 6:
            flash("Preencha nome, email e uma senha com pelo menos 6 caracteres.")
            return render_template("registrar.html")

        conn = get_connection_db()
        existente = conn.execute(
            "SELECT id FROM usuarios WHERE email = ?", (email,)
        ).fetchone()

        if existente:
            conn.close()
            flash("Já existe uma conta com esse email.")
            return render_template("registrar.html")

        senha_hash = generate_password_hash(senha)
        cursor = conn.execute(
            "INSERT INTO usuarios (nome, email, senha_hash) VALUES (?, ?, ?)",
            (nome, email, senha_hash),
        )
        conn.commit()
        novo_id = cursor.lastrowid
        conn.close()

        login_user(Usuario({"id": novo_id, "nome": nome, "email": email}))
        return redirect(url_for("home"))

    return render_template("registrar.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("welcome"))


def _tabela_existe(conn, nome_tabela):
    resultado = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name = ?",
        (nome_tabela,),
    ).fetchone()
    return resultado is not None


def _tabelas_de_jogos(conn):
    tabelas = ["jogos_brutos"]
    if _tabela_existe(conn, "promocoes_steam"):
        tabelas.append("promocoes_steam")
    return tabelas


def obter_promocoes_da_wishlist(conn, usuario_id, limite=12):
    tabelas = _tabelas_de_jogos(conn)
    uniao = " UNION ALL ".join(f"SELECT * FROM {t}" for t in tabelas)
    query = f"""
        SELECT d.*
        FROM ({uniao}) AS d
        INNER JOIN wishlist w
            ON CAST(w.game_id AS TEXT) = CAST(d.Game_ID AS TEXT)
        WHERE w.usuario_id = ? AND d.Discount_Percent > 0
        ORDER BY d.Discount_Percent DESC
        LIMIT ?
    """
    linhas = conn.execute(query, (usuario_id, limite)).fetchall()
    return [dict(linha) for linha in linhas]


def obter_catalogo(conn, busca="", offset=0, limite=GAMES_POR_PAGINA):
    filtro = ""
    params = []
    if busca:
        filtro = "WHERE Title LIKE ?"
        params.append(f"%{busca}%")

    query = f"""
        SELECT
            Game_ID,
            Title,
            MAX(Thumb) AS Thumb,
            MAX(Metacritic_Score) AS Metacritic_Score
        FROM jogos_brutos
        {filtro}
        GROUP BY Title
        ORDER BY Title
        LIMIT ? OFFSET ?
    """
    params.extend([limite, offset])
    linhas = conn.execute(query, params).fetchall()
    return [dict(linha) for linha in linhas]


def obter_wishlist_ids(conn, usuario_id):
    linhas = conn.execute(
        "SELECT game_id FROM wishlist WHERE usuario_id = ?", (usuario_id,)
    ).fetchall()
    return {str(linha["game_id"]) for linha in linhas}


@app.route("/")
@login_required
def home():
    conn = get_connection_db()
    promocoes = obter_promocoes_da_wishlist(conn, int(current_user.id))
    conn.close()
    return render_template("homepage.html", promocoes=promocoes)


@app.route("/jogos")
@login_required
def jogos():
    conn = get_connection_db()
    catalogo = obter_catalogo(conn)
    favoritos = obter_wishlist_ids(conn, int(current_user.id))
    conn.close()
    return render_template(
        "jogos.html",
        catalogo=catalogo,
        favoritos=favoritos,
        games_por_pagina=GAMES_POR_PAGINA,
    )


@app.route("/api/jogos", methods=["GET"])
@login_required
def api_jogos():
    busca = request.args.get("q", "").strip()
    offset = int(request.args.get("offset", 0))

    conn = get_connection_db()
    catalogo = obter_catalogo(conn, busca=busca, offset=offset)
    favoritos = obter_wishlist_ids(conn, int(current_user.id))
    conn.close()

    for jogo in catalogo:
        jogo["favoritado"] = str(jogo["Game_ID"]) in favoritos

    return jsonify(catalogo)


@app.route("/api/jogos/<game_id>", methods=["GET"])
@login_required
def api_jogo_detalhe(game_id):
    conn = get_connection_db()
    tabelas = _tabelas_de_jogos(conn)
    uniao = " UNION ALL ".join(f"SELECT * FROM {t}" for t in tabelas)
    query = f"SELECT * FROM ({uniao}) WHERE CAST(Game_ID AS TEXT) = ?"
    linhas = conn.execute(query, (str(game_id),)).fetchall()
    favoritos = obter_wishlist_ids(conn, int(current_user.id))
    conn.close()

    return jsonify({
        "game_id": game_id,
        "favoritado": str(game_id) in favoritos,
        "ofertas": [dict(linha) for linha in linhas],
    })


@app.route("/api/wishlist/toggle", methods=["POST"])
@login_required
def api_wishlist_toggle():
    dados = request.get_json(force=True)
    game_id = str(dados.get("game_id"))
    titulo = dados.get("titulo")
    thumb = dados.get("thumb")
    usuario_id = int(current_user.id)

    conn = get_connection_db()
    ja_existe = conn.execute(
        "SELECT id FROM wishlist WHERE usuario_id = ? AND game_id = ?",
        (usuario_id, game_id),
    ).fetchone()

    if ja_existe:
        conn.execute(
            "DELETE FROM wishlist WHERE usuario_id = ? AND game_id = ?",
            (usuario_id, game_id),
        )
        favoritado = False
    else:
        conn.execute(
            "INSERT INTO wishlist (usuario_id, game_id, titulo, thumb) VALUES (?, ?, ?, ?)",
            (usuario_id, game_id, titulo, thumb),
        )
        favoritado = True

    conn.commit()
    conn.close()

    return jsonify({"favoritado": favoritado})


if __name__ == "__main__":
    app.run(debug=True)
