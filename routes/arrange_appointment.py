from app import app
from helpers import login_required, appointmentAlreadyArranged, checkUserInfo, db
from flask import render_template, redirect, request
from datetime import date, datetime

@app.route("/arrange-appointment/<id>", methods=["GET", "POST"])
@login_required
def arrangeAppointment(id):
    info = checkUserInfo()
    sameUser = info["id"] == int(id)
    isChef = True
    chefInfo = db.execute("SELECT * from chefs WHERE user_id == ?", id)
    try:
        chefInfo[0]
    except:
        isChef = False

    if sameUser:
        return render_template("arrange-appointment.html", id=id, sameUser=sameUser, isChef=isChef, info=info, error="You can not arrange an appointment to your profile")
    if not isChef:
        return render_template("arrange-appointment.html", id=id, sameUser=sameUser, isChef=isChef, info=info, error="You can only arrange an appointment to a chef")

    if request.method == "POST":
        people = request.form.get("people")
        if not people or int(people) <= 0:
            return render_template("arrange-appointment.html", id=id, sameUser=sameUser, isChef=isChef, info=info, error="Invalid number of people")

        currentDate = date.today()
        arrangedDate = request.form.get("date")
        arrangedDateObject = datetime.strptime(arrangedDate, '%Y-%m-%d').date()
        if not date or arrangedDateObject < currentDate:
            return render_template("arrange-appointment.html", id=id, sameUser=sameUser, isChef=isChef, info=info, error="Invalid date")
        if appointmentAlreadyArranged(id, arrangedDateObject):
            return render_template("arrange-appointment.html", id=id, sameUser=sameUser, isChef=isChef, info=info, error="You can not arrange an appointment with the same chef at the same date")

        return redirect("/confirm/"+str(id)+"/"+str(people)+"/"+str(arrangedDate))
    else:
        return render_template("arrange-appointment.html", id=id, sameUser=sameUser, isChef=isChef, info=info)