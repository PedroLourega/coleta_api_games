from flask import Flask, jsonify, render_template
import sqlite3


def get_connection_db():
    conn = sqlite3.connect("databases/db.sqlite3")
    conn.row_factory = sqlite3.Row
    return conn
