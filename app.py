from flask import Flask, request, redirect, make_response, render_template_string
from werkzeug.security import check_password_hash

app = Flask(__name__)

# Replace this with your actual hashed password
HASHED_PASSWORD = 'pbkdf2:sha256:260000$X$Y'  # Use generate_password_hash()

@app.route("/expert-mode")
def expert_mode():
    if request.cookies.get("admin") == "1":
        return "<h1>Welcome to Expert Mode!</h1><a href='/logout'>Logout</a>"
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        pwd = request.form["password"]
        if check_password_hash(HASHED_PASSWORD, pwd):
            resp = make_response(redirect("/expert-mode"))
            resp.set_cookie("admin", "1", httponly=True, secure=True, max_age=3600)
            return resp
        return "Incorrect password", 403

    return render_template_string('''
        <form method="POST">
            <input type="password" name="password" placeholder="Enter password">
            <button type="submit">Login</button>
        </form>
    ''')

@app.route("/logout")
def logout():
    resp = make_response(redirect("/login"))
    resp.set_cookie("admin", "", expires=0)
    return resp

if __name__ == "__main__":
    app.run()
