import sqlite3
from flask import Flask, request, render_template, send_file
import hashlib
import re
import subprocess


def get_git_revision_short_hash() -> str:
    return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()

expression = "^(https?:\/?\/?)?[a-z?A-Z?0-9?_?\-]+\.?[a-zA-Z0-9_\-]+\.[a-zAZ0-9_\-]+/?.*$"

app = Flask(__name__)
db = sqlite3.connect('URLs.db', check_same_thread=False)
cur = db.cursor()
try:
    cur.execute('CREATE TABLE URLs (url TEXT, hash TEXT)')
except:
    print("Table already exists, continuing...")


@app.route('/')
def index():
    return render_template('index.html', commit_hash=get_git_revision_short_hash())

@app.route("/static/<file>")
def static_file(file):
    return send_file(f"static/{file}")


@app.route("/resolve/<short>")
def resolve(short):
    cur.execute("SELECT url FROM URLs WHERE hash=?", (short,))
    result = cur.fetchone()
    if result:
        return result[0]
    else:
        return "Not Found"


@app.route("/shorten", methods=['POST'])
def shorten():
    url = request.form['url']
    if not re.match(expression, url):
        return "Invalid URL"
    hash = hashlib.sha512(url.encode('utf-8')).hexdigest()[:6]
    cur.execute("SELECT * FROM URLs WHERE url=?", (url,))
    result = cur.fetchone()
    if result:
        return result[0]
    else:
        cur.execute("INSERT INTO URLs (url,hash) VALUES (?,?)", (url, hash,))
        db.commit()
        cur.execute("SELECT * FROM URLs WHERE url=?", (url,))
        result = cur.fetchone()
        return result[1]


if __name__ == "__main__":
    app.run(debug=True)
