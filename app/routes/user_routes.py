from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    jsonify,
)
from app.utils.db_utils import get_db_connection
from app.utils.auth_utils import login_required
from datetime import datetime

user_bp = Blueprint("user", __name__)


@user_bp.route("/user_signup", methods=["POST", "GET"])
def user_signup():

    if request.method == "POST":
        name = request.form["name"]
        location = request.form["location"]
        email = request.form["email"]
        password = request.form["password"]

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user WHERE user_email = %s", (email,))
            account = cursor.fetchone()

            if account:
                print("Account already exists!")
            else:
                cursor.execute(
                    "INSERT INTO user (user_name, user_email, user_password, user_location) VALUES (%s, %s, %s, %s)",
                    (name, email, password, location),
                )
                print("Account created successfully!")
                conn.commit()

        except Exception as e:
            print(f"Error: {e}")

        finally:
            conn.close()

        return redirect(url_for("user.user_login"))

    return render_template("user_signup.html")


@user_bp.route("/user_login", methods=["POST", "GET"])
def user_login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM user WHERE user_email = %s", (email,))
            account = cursor.fetchone()

            if account and account["user_password"] == password:
                session.update(
                    {
                        "loggedin": True,
                        "id": account["user_id"],
                        "role": "user",
                        "username": account["user_name"],
                        "email": account["user_email"],
                        "points": account["user_points"],
                        "date": account["user_joining_date"],
                    }
                )
                print("Login successful!")
                return redirect(url_for("user.user_dashboard"))
            else:
                print("Incorrect username/password!")

        except Exception as e:
            print(f"Error: {e}")
        finally:
            conn.close()

    return render_template("user_login.html")


@user_bp.route("/user_submit", methods=["POST", "GET"])
@login_required
def user_submit():
    if request.method == "POST":
        branch = request.form["branch"]
        plastic_quantity = request.form.get("plastic-quantity", 0, type=int)
        cardboard_quantity = request.form.get("cardboard-quantity", 0, type=int)
        glass_quantity = request.form.get("glass-quantity", 0, type=int)

        user_id = session.get("id")
        if not user_id:
            print("Please log in to submit an order.")
            return redirect(url_for("user_login"))

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Insert submission with separate values
            cursor.execute(
                """
                INSERT INTO user_history (user_id, plastic_bottles, cardboards, glasses, user_history_date, user_history_branch) 
                VALUES (%s, %s, %s, %s, NOW(), %s)
                """,
                (user_id, plastic_quantity, cardboard_quantity, glass_quantity, branch),
            )

            # Update the storage
            cursor.execute(
                """
                UPDATE storage
                SET
                    plastic = plastic + %s,
                    cardboard = cardboard + %s,
                    glass = glass + %s
                """,
                (plastic_quantity, cardboard_quantity, glass_quantity),
            )

            # Calculate points based on material type
            plastic_points = plastic_quantity * 2  # 2 points per bottle
            cardboard_points = cardboard_quantity * 1  # 1 point per cardboard
            glass_points = glass_quantity * 3  # 3 points per glass
            total_points = plastic_points + cardboard_points + glass_points

            # Update user points in the database
            cursor.execute(
                "UPDATE user SET user_points = user_points + %s WHERE user_id = %s",
                (total_points, user_id),
            )

            # Update session with new points total
            session["points"] = session.get("points", 0) + total_points

            conn.commit()
            print("Submission successful!")

        except Exception as e:
            print(f"Error: {e}")
            print("An error occurred during submission.")

        finally:
            conn.close()

        return redirect(url_for("user.user_dashboard"))

    return render_template("user_dashboard.html")


@user_bp.route("/user_dashboard")
@login_required("user")
def user_dashboard():
    username = session.get("username")
    user_id = session.get("id")
    points = session.get("points")
    date = session.get("date")

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Get user location
        cursor.execute("SELECT user_location FROM user WHERE user_id = %s", (user_id,))
        user_data = cursor.fetchone()
        location = user_data.get("user_location", "") if user_data else ""

        # Fetch submission history with separate columns
        cursor.execute(
            """
            SELECT user_history_date, plastic_bottles, cardboards, glasses, user_history_branch 
            FROM user_history 
            WHERE user_id = %s 
            ORDER BY user_history_date DESC
            """,
            (user_id,),
        )
        submissions = cursor.fetchall()

        cursor.execute(
            """
                SELECT 
                    SUM(plastic_bottles), 
                    SUM(cardboards), 
                    SUM(glasses) 
                FROM user_history
                WHERE user_id = %s
            """,
            (user_id,),
        )
        summary = cursor.fetchone()

        # Assign values to variables
        total_plastic, total_cardboards, total_glasses = summary.values()

    except Exception as e:
        print(f"Error: {e}")
        submissions = []
        location = ""

    finally:
        conn.close()

    date_obj = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S GMT")
    formatted_date = date_obj.strftime("%B %d, %Y")

    return render_template(
        "user_dashboard.html",
        username=username,
        email=session.get("email"),
        date=formatted_date,
        points=points,
        location=location,
        submissions=submissions,
        total_plastic=total_plastic,
        total_cardboards=total_cardboards,
        total_glasses=total_glasses,
    )
