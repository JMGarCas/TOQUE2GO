from flask import request, redirect, render_template, session
from app import app
from helpers import login_required, checkUserInfo, db

@app.route("/appointments", methods=["GET", "POST"])
@login_required
def appointments():
    info = checkUserInfo()
    appointments = db.execute("SELECT * FROM users JOIN appointments ON appointments.client_id == users.id WHERE appointments.user_id == ?", session["user_id"])
    appointmentsSend = db.execute("SELECT * FROM users JOIN appointments ON appointments.user_id == users.id WHERE appointments.client_id == ?", session["user_id"])
    appointments.extend(appointmentsSend)
    appointments = sorted(appointments, key=lambda x:x["id"], reverse=True)

    if request.method == "POST":
        return redirect("/")
    else:
        return render_template("appointments.html", info=info, appointments=appointments)