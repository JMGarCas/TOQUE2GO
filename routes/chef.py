from flask import render_template, request, redirect, session
from app import app
from helpers import login_required, checkUserInfo, db   
from constants import allTypes

@app.route("/chef", methods=["GET", "POST"])
@login_required
def chef():
    info = checkUserInfo()
    if request.method == "POST":

        types = request.form.getlist('type')
        if len(types) < 1:
            return render_template("chef.html", info=info, error="Select at least one type of food")
        if len(types) != len(set(types)):
            return render_template("chef.html", info=info, error="Select distinct types of food")

        cost = request.form.get('cost')
        if not cost or float(cost) <= 0.0:
            return render_template("chef.html", info=info, error="Invalid cost value")

        information = request.form.get('information')
        if not information:
            return render_template("chef.html", info=info, error="Please tell us about yourself")

        db.execute("DELETE FROM chefs WHERE user_id = ?", session["user_id"])

        for type in types:
            if type in allTypes:
                db.execute("INSERT INTO chefs (user_id, type, cost, information) VALUES (?, ?, ?, ?)",session["user_id"], type, float(cost), information)
        return redirect("/")
    else:
        return render_template("chef.html", info=info)