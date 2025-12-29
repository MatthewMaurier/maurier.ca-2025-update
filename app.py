from flask import Flask, request, redirect, make_response, render_template, send_from_directory, abort
from pathlib import Path
from urllib.parse import quote
from werkzeug.security import check_password_hash

app = Flask(__name__)

# Set your hashed password
VALID_USERNAME = "admin"
HASHED_PASSWORD = 'pbkdf2:sha256:260000$IUU74iQCAMUVntHe$43cb546ad35de9245c9b50f281724c27e1b591f4e3ac2b210ba267bd0f3769ec'  # Replace with real hash

### ROUTES ###

# Serve root (index.html)
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

# Serve all .html files from root
@app.route('/<path:filename>')
def serve_file(filename):
    if filename.endswith('.html'):
        return send_from_directory('.', filename)
    return send_from_directory('.', filename)

# Serve /expert-mode from Flask template if logged in
@app.route("/expert-mode")
def expert_mode():
    if request.cookies.get("admin") == "1":
        resp = make_response(render_template("expert-mode.html"))
        # Refresh the cookie on each access (sliding expiration)
        resp.set_cookie("admin", "1", httponly=True, secure=False, max_age=60 * 60 * 24 * 365)
        return resp
    return redirect("/login")


# Login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        remember = request.form.get("remember") == "on"

        if username == VALID_USERNAME and check_password_hash(HASHED_PASSWORD, password):
            resp = make_response(redirect("/expert-mode"))
            max_age = 60 * 60 * 24 * 365 if remember else 60 * 60  # 1 year or 1 hour
            resp.set_cookie("admin", "1", httponly=True, secure=False, max_age=max_age)
            return resp

        return "Incorrect username or password", 403

    return render_template("login.html")

# Logout route
@app.route("/logout")
def logout():
    resp = make_response(redirect("/login"))
    resp.set_cookie("admin", "", expires=0)
    return resp


PHOTO_ROOT = Path("archive_files").resolve()

IMG_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
VID_EXTS = {".mp4", ".webm", ".mov", ".m4v", ".ogg"}  # ogg can be video too

def file_kind(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in IMG_EXTS:
        return "image"
    if ext in VID_EXTS:
        return "video"
    return "other"

@app.route("/archive")
def gallery_index():
    albums = sorted(p.name for p in PHOTO_ROOT.iterdir() if p.is_dir())
    return render_template("archive.html", albums=albums)

@app.route("/archive/<album>")
def gallery_album(album):
    album_path = (PHOTO_ROOT / album).resolve()
    if not album_path.is_dir() or not str(album_path).startswith(str(PHOTO_ROOT)):
        abort(404)

    # include ALL files (images, videos, and other)
    items = []
    for p in sorted(album_path.iterdir(), key=lambda x: x.name.lower()):
        if p.is_file():
            items.append({
                "name": p.name,
                "kind": file_kind(p),
                "url_name": quote(p.name)  # safe for spaces/#/etc in URLs
            })

    return render_template("album.html", album=album, items=items)

@app.route("/archive/<album>/<path:filename>")
def file_serve(album, filename):
    album_path = (PHOTO_ROOT / album).resolve()
    if not str(album_path).startswith(str(PHOTO_ROOT)):
        abort(404)
    return send_from_directory(album_path, filename, as_attachment=False)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)


