from app import app
from helpers import login_required, checkUserInfo, db
from flask import redirect, render_template

@app.route("/delete/<id>")
@login_required
def delete(id):
    info = checkUserInfo()
    if info["isAdmin"]:
        db.execute("DELETE FROM reviews WHERE writer_id = ? OR user_id = ?", id, id)
        db.execute("DELETE FROM appointments WHERE client_id = ? OR user_id = ?", id, id)
        db.execute("DELETE FROM chefs WHERE user_id = ?", id)
        db.execute("DELETE FROM users WHERE id = ?", id)

        return redirect("/users")
    else:
        return render_template("users.html", id=id, info=info, error="You do not have permissions here")