from flask import render_template, redirect
from app import app
from helpers import login_required, checkUserInfo, db

@app.route("/accept/<id>")
@login_required
def accept(id):
    info = checkUserInfo()
    appointment = db.execute("SELECT * FROM appointments WHERE id == ?", id)
    try:
        if appointment[0]["user_id"] != info["id"]:
            return render_template("appointments.html", info=info, error="You do not have permissions in this appointment")
        if appointment[0]["status"] == "waiting":
            db.execute("UPDATE appointments SET status = 'accepted' WHERE id = ?", id)
            redirect("/appointments")
        else:
            return render_template("appointments.html", info=info, error="Appointment already accepted or declined")
    except:
        return render_template("appointments.html", info=info, error="Appointment with id "+str(id)+" does not exist")

    return redirect("/appointments")