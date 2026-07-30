import sqlite3
from pathlib import Path

CAMINHO_DB = Path(__file__).parent / "databases" / "db.sqlite3"


def get_connection_db():
    conn = sqlite3.connect(CAMINHO_DB)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection_db()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            senha_hash TEXT NOT NULL,
            criado_em TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS wishlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            game_id TEXT NOT NULL,
            titulo TEXT,
            thumb TEXT,
            criado_em TEXT DEFAULT (datetime('now')),
            UNIQUE(usuario_id, game_id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        );
        """
    )
    conn.commit()
    conn.close()
