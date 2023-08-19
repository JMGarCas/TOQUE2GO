from flask import render_template, request, session, redirect
from app import app
from helpers import db   
from constants import locations
from werkzeug.security import generate_password_hash

@app.route("/register", methods=["GET", "POST"])
def register():

    session.clear()

    """Register user"""
    if request.method == "POST":

        email = request.form.get("email")
        if len(db.execute("SELECT * FROM users WHERE email = ?", email)) != 0:
            return render_template("register.html", error="Email already registered")
        if not email:
            return render_template("register.html", error="Blank email")

        name = request.form.get("name")
        surname = request.form.get("surname")
        if not name:
            return render_template("register.html", error="Blank name")
        if not surname:
            return render_template("register.html", error="Blank surname")

        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if not password:
            return render_template("register.html", error="Blank password")
        elif confirmation != password:
            return render_template("register.html", error="Password not equal to confirmation")

        location = request.form.get("location")
        if location not in locations:
            return render_template("register.html", error="Invalid location")

        hash = generate_password_hash(password)
        db.execute("INSERT INTO users (email, name, surname, hash, location, profile, banner) VALUES(?, ?, ?, ?, ?, ?, ?)", email, name, surname, hash, location, "/static/default-profile.png", "/static/default-banner.jpg")
        return redirect("/login")

    else:
        return render_template("register.html", locations=locations)