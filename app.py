from flask import Flask, request, jsonify, render_template

app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@app.route("/login")
def login_general():
    return render_template("login_general.html")


@app.route("/user_login")
def login_user():
    return render_template("user_signup.html")


@app.route("/user_signup")
def signup_user():
    return render_template("user_signup.html")


@app.route("/company_login")
def login_company():
    return render_template("company_login.html")


@app.route("/company_signup")
def signup_company():
    return render_template("company_signup.html")


@app.route("/find_bins")
def find_bins():
    return render_template("find_bin.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
