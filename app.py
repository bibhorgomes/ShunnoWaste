from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import mysql.connector 

app = Flask(__name__)


def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="db_shunnowaste",
    )
    return connection


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@app.route("/login")
def login_general():
    return render_template("login_general.html")


@app.route("/user_login")
def login_user():
    return render_template("user_login.html")


@app.route("/user_signup")
def signup_user():
    return render_template("user_signup.html")


@app.route("/company_signup", methods=["POST", "GET"])
def company_signup():
    if request.method == "POST":
        company_name = request.form["company_name"]
        company_location = request.form["company_location"]
        email = request.form["email"]
        password = request.form["password"]
        print("Hello")

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM company WHERE company_email = %s", (email,))
            account = cursor.fetchone()

            if account:
                print("Company account already exists!")
            else:
                cursor.execute(
                    "INSERT INTO company (company_name, company_email, company_password, company_location) VALUES (%s, %s, %s, %s)",
                    (company_name, email, password, company_location),
                )
                print("Company account created successfully!")
                conn.commit()

        except Exception as e:
            print(f"Error: {e}")

        finally:
            conn.close()

        return redirect(url_for("company_login"))

    return render_template("company_signup.html")


@app.route("/company_login", methods=["POST", "GET"])
def company_login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM company WHERE company_email = %s", (email,))
            account = cursor.fetchone()

            if account and account["company_password"] == password:
                session.update(
                    {
                        "loggedin": True,
                        "company_id": account["company_id"],
                        "company_name": account["company_name"],
                        "company_email": account["company_email"],
                        "company_location": account["company_location"],
                    }
                )
                print("Company login successful!")
                return redirect(url_for("company_dashboard"))
            else:
                print("Incorrect email/password!")

        except Exception as e:
            print(f"Error: {e}")
        finally:
            conn.close()

    return render_template("company_login.html")



@app.route("/company_dashboard", methods=["POST", "GET"])
@login_required
def company_dashboard():
    company_name = session.get("company_name")
    company_email = session.get("company_email")
    company_location = session.get("company_location")
    company_date = session.get("company_date")

    if session.get("loggedin"):
        return render_template(
            "company_dashboard.html", company_name=company_name, company_email=company_email, company_location = company_location, company_date=company_date
        )
    else:
        return redirect(url_for("company_login"))


@app.route("/find_bins")
def find_bins():
    return render_template("find_bin.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
