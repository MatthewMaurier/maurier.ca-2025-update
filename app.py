from flask import Flask, request, redirect, make_response, render_template, send_from_directory
from werkzeug.security import check_password_hash

app = Flask(__name__)

# Set your hashed password
VALID_USERNAME = "admin"
HASHED_PASSWORD = 'pbkdf2:sha256:260000$HKxK41GmrqafhOzs$82fc959facaa67c084616e6a99341074a4468695a8778698aa95b9190ffee5f0'  # Replace with real hash

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)