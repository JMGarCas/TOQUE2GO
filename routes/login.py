from flask import render_template, request, session, redirect
from app import app
from helpers import db   
from werkzeug.security import check_password_hash

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure email was submitted
        if not request.form.get("email"):
            return render_template("login.html", error="Must provide an email")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("login.html", error="Must provide a password")

        # Query database for email
        rows = db.execute(
            "SELECT * FROM users WHERE email = ?", request.form.get("email")
        )

        # Ensure email exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return render_template("login.html", error="Invalid email and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")