from flask import render_template, request, redirect, session
from app import app
from helpers import login_required, checkUserInfo, db   

@app.route("/premium", methods=["GET", "POST"])
@login_required
def premium():
    info = checkUserInfo()
    if info["isPremium"] == True:
        return render_template("premium.html", info=info, error="You are already a premium user")
    if request.method == "POST":
        db.execute("UPDATE users SET membership = 'premium' WHERE id = ?", session["user_id"])
        return redirect("/")
    else:
        return render_template("premium.html", info=info)