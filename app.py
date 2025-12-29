from flask import Flask, request, redirect, make_response, render_template, send_from_directory, abort
from pathlib import Path
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


PHOTO_ROOT = Path("/data/photos").resolve()
IMG_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

@app.route("/gallery")
def gallery_index():
    albums = sorted(
        p.name for p in PHOTO_ROOT.iterdir()
        if p.is_dir()
    )
    return render_template("gallery.html", albums=albums)

@app.route("/gallery/<album>")
def gallery_album(album):
    album_path = (PHOTO_ROOT / album).resolve()
    if not album_path.is_dir() or not str(album_path).startswith(str(PHOTO_ROOT)):
        abort(404)

    images = sorted(
        p.name for p in album_path.iterdir()
        if p.suffix.lower() in IMG_EXTS
    )

    return render_template(
        "album.html",
        album=album,
        images=images
    )

@app.route("/photos/<album>/<filename>")
def photo(album, filename):
    album_path = (PHOTO_ROOT / album).resolve()
    if not str(album_path).startswith(str(PHOTO_ROOT)):
        abort(404)
    return send_from_directory(album_path, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)


