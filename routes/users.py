from app import app
from helpers import login_required, checkUserInfo, db
from flask import render_template

@app.route("/users")
@login_required
def users():
    info = checkUserInfo()
    if info["isAdmin"]:
        users = db.execute("SELECT * FROM users")
        return render_template("users.html", id=id, info=info, users=users)
    else:
        return render_template("users.html", id=id, info=info, error="You do not have permissions here")