import sqlite3
from app.config import Config
from app.modules.git_tools import get_git_revision_short_hash
from flask import Flask, request, render_template, send_file, redirect

app = Flask(__name__)
db = sqlite3.connect('URLs.db', check_same_thread=False)
cur = db.cursor()
config = Config()

for vanity_url in config.vanity_urls:
    print(f"{vanity_url}:{config.vanity_urls[vanity_url]}")
try:
    cur.execute('CREATE TABLE URLs (url TEXT unique, hash TEXT PRIMARY KEY)')
except Exception as e:
    print(f'A DB error occurred: {e}')

for vanity_url in config.vanity_urls:
    key = vanity_url
    val = config.vanity_urls[vanity_url]
    try:
        cur.execute("INSERT INTO URLs (url,hash) VALUES (?,?)", (val, key,))
        db.commit()
    except Exception as e:
        print(f'A DB error occurred: {e}')

from app.routes import *
