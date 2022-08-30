import sqlite3
from flask import Flask, request, render_template, send_file, redirect
import hashlib
import re
import subprocess


def get_git_revision_short_hash() -> str:
    return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()


expression = "^(https?:\/\/)?[a-zA-Z0-9_\-]+(\.[a-zAZ0-9_\-]+)+(\/.*)?$"

vanity_urls = {
    "resin": "https://explorer.resincoin.ml",
    "ssniper1": "https://ssniper1.ml",
    "murka": "https://murkauserbot.ml",
    "gay": "https://t.me/gdlbo",
}

app = Flask(__name__)
db = sqlite3.connect('URLs.db', check_same_thread=False)
cur = db.cursor()
for vanityurl in vanity_urls:
        print(f"{vanityurl}:{vanity_urls[vanityurl]}")
try:
    cur.execute('CREATE TABLE URLs (url TEXT unique, hash TEXT PRIMARY KEY)')
except:
    pass

for vanityurl in vanity_urls:
    key = vanityurl
    val = vanity_urls[vanityurl]
    try:
        cur.execute("INSERT INTO URLs (url,hash) VALUES (?,?)", (val, key,))
        db.commit()
    except:
        pass


@app.route('/')
def index():
    return render_template('index.html', commit_hash=get_git_revision_short_hash())


@app.route("/static/<file>")
def static_file(file):
    return send_file(f"static/{file}")


@app.route("/resolve/<short>")
def resolve(short):
    cur.execute("SELECT url FROM URLs WHERE hash LIKE ?", (short,))
    result = cur.fetchone()
    if result:
        return result[0]
    else:
        return "Not Found"


@app.route("/shorten", methods=['POST', 'GET'])
def shorten():
    if request.method == "GET":
        return redirect("/")
    url = request.form['url']
    if not re.match(expression, url):
        return "Invalid URL"
    hash = hashlib.sha512(url.encode('utf-8')).hexdigest()[:6]
    cur.execute("SELECT hash FROM URLs WHERE url=?", (url,))
    result = cur.fetchone()
    if result:
        return render_template("shorted.html", short=result[0])
    else:
        cur.execute("INSERT INTO URLs (url,hash) VALUES (?,?)", (url, hash,))
        db.commit()
        cur.execute("SELECT * FROM URLs WHERE url=?", (url,))
        result = cur.fetchone()
        return render_template("shorted.html", short=result[1])

@app.route("/<short>")
def redirect_to_short(short):
    url = cur.execute("SELECT url FROM URLs WHERE hash LIKE ?", (short,))
    url = cur.fetchone()[0]
    if url.startswith("http") or url.startswith("https"):
        return redirect(url)
    else:
        return redirect(f"http://{url}")

if __name__ == "__main__":
    app.run()
