from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    jsonify,
)
from app.utils.db_utils import get_db_connection
from app.utils.auth_utils import login_required

company_bp = Blueprint("company", __name__)


@company_bp.route("/company_submit", methods=["POST"])
@login_required("company")
def company_submit():
    if request.method == "POST":
        plastic_quantity = request.form.get("plasticBottles", 0, type=int)
        cardboard_quantity = request.form.get("cardboard", 0, type=int)
        glass_quantity = request.form.get("glass", 0, type=int)
        company_id = session.get("company_id")

        if not company_id:
            return redirect(url_for("company.company_login"))

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO company_history 
                (company_id, plastic_bottles, cardboards, glasses) 
                VALUES (%s, %s, %s, %s)
                """,
                (company_id, plastic_quantity, cardboard_quantity, glass_quantity),
            )

            cursor.execute(
                """
                UPDATE storage
                SET
                    plastic = plastic - %s,
                    cardboard = cardboard - %s,
                    glass = glass - %s
                """,
                (plastic_quantity, cardboard_quantity, glass_quantity),
            )
            conn.commit()

        except Exception as e:
            print(f"Error: {e}")

        finally:
            conn.close()

        return redirect(url_for("company.company_dashboard"))

    return render_template("company_dashboard.html")


@company_bp.route("/company_signup", methods=["POST", "GET"])
def company_signup():
    if request.method == "POST":
        company_name = request.form["company_name"]
        company_location = request.form["company_location"]
        email = request.form["email"]
        password = request.form["password"]

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM company WHERE company_email = %s", (email,))
            account = cursor.fetchone()

            if account:
                print("Company account already exists!")
            else:
                cursor.execute(
                    "INSERT INTO company (company_name, company_location, company_email, company_password) VALUES (%s, %s, %s, %s)",
                    (company_name, company_location, email, password),
                )
                print("Company account created successfully!")
                conn.commit()
        except Exception as e:
            print(f"Error: {e}")
        finally:
            conn.close()
        return redirect(url_for("company.company_login"))
    return render_template("company_signup.html")


@company_bp.route("/company_login", methods=["POST", "GET"])
def company_login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM company WHERE company_email = %s", (email,))
            account = cursor.fetchone()

            if account[3] == password:
                print("Password matched!")
                session["loggedin"] = True
                session["company_id"] = account[0]
                session["company_name"] = account[1]
                session["company_email"] = email
                session["company_location"] = account[4]
                session["role"] = "company"  # Add this line to set the role
                print("Company logged in successfully!")
                return redirect(url_for("company.company_dashboard"))
            else:
                print("Incorrect email/password!")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            conn.close()

    return render_template("company_login.html")


@company_bp.route("/company_dashboard")
@login_required("company")
def company_dashboard():
    company_name = session.get("company_name", "Company")
    company_id = session.get("company_id", "ID")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch stock data from storage
        cursor.execute("SELECT plastic, cardboard, glass FROM storage LIMIT 1")
        stock_data = cursor.fetchone()
        stock = {
            "Plastic": stock_data[0],
            "Cardboard": stock_data[1],
            "Glass": stock_data[2],
        }

        # Fetch company history with separate columns for materials
        cursor.execute(
            """
            SELECT company_history_date, plastic_bottles, cardboards, glasses
            FROM company_history
            WHERE company_id = %s
            ORDER BY company_history_date DESC
            """,
            (company_id,),
        )
        history_data = cursor.fetchall()
        history_data = [
            {
                "company_history_date": row[0],
                "plastic_bottles": row[1],
                "cardboards": row[2],
                "glasses": row[3],
            }
            for row in history_data
        ]

        cursor.execute(
            """
                SELECT 
                    SUM(plastic_bottles), 
                    SUM(cardboards), 
                    SUM(glasses) 
                FROM company_history
                WHERE company_id = %s
            """,
            (company_id,),
        )
        summary = cursor.fetchone()
        total_plastic, total_cardboards, total_glasses = summary

    except Exception as e:
        print(f"Error: {e}")
        stock = {"Plastic": 0, "Cardboard": 0, "Glass": 0}
        history_data = []
    finally:
        conn.close()

    return render_template(
        "company_dashboard.html",
        company_name=company_name,
        company_location=session["company_location"],
        stock_data=stock,
        history_data=history_data,
        total_plastic=total_plastic,
        total_cardboards=total_cardboards,
        total_glasses=total_glasses,
    )
