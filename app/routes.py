import re
import hashlib

from app import get_git_revision_short_hash, cur, db, config
from app import app, render_template, send_file, request, redirect


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
    if not re.match(config.expression, url):
        return "Invalid URL"
    url_hash = hashlib.sha512(url.encode('utf-8')).hexdigest()[:6]
    cur.execute("SELECT hash FROM URLs WHERE url=?", (url,))
    result = cur.fetchone()
    if result:
        return render_template("shorted.html", short=result[0])
    else:
        cur.execute("INSERT INTO URLs (url,hash) VALUES (?,?)", (url, url_hash,))
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
