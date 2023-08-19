from app import app
from helpers import login_required, checkUserInfo, calculateCost, sameLocation, appointmentAlreadyArranged, db
from datetime import date, datetime
from flask import render_template, request, session, redirect

@app.route("/confirm/<id>/<people>/<dateS>", methods=["GET", "POST"])
@login_required
def confirm(id, people, dateS):
    info = checkUserInfo()
    sameUser = info["id"] == int(id)
    isChef = True
    chefInfo = db.execute("SELECT * from chefs WHERE user_id == ?", id)
    try:
        chefInfo[0]
    except:
        isChef = False

    if sameUser:
        return render_template("confirm.html", id=id, info=info, error="You can not arrange an appointment to your profile")
    if not isChef:
        return render_template("confirm.html", id=id, info=info, error="You can only arrange an appointment to a chef")
    if int(people) <= 0:
            return render_template("confirm.html", id=id, info=info, error="Invalid number of people")

    currentDate = date.today()
    arrangedDate = dateS
    arrangedDateObject = datetime.strptime(arrangedDate, '%Y-%m-%d').date()
    if not date or arrangedDateObject < currentDate:
        return render_template("confirm.html", id=id, info=info, error="Invalid date")
    if appointmentAlreadyArranged(id, arrangedDateObject):
        return render_template("confirm.html", id=id, info=info, error="You can not arrange an appointment with the same chef at the same date")

    cost = db.execute("SELECT DISTINCT * FROM chefs WHERE user_id = ?", id)[0]["cost"]
    costs = calculateCost(id, int(people), float(cost))

    if request.method == "POST":
        selection = request.form['selection']
        if selection == "accepted":
            db.execute("INSERT INTO appointments (client_id, user_id, date, people, cost) VALUES (?, ?, ?, ?, ?)", session["user_id"], id, arrangedDateObject, int(people), costs["totalCost"])
            return redirect("/profile/"+str(id))
        elif selection == "declined":
            return redirect("/profile/"+str(id))
        else:
            render_template("confirm.html", id=id, info=info, error="Select a valid value")
    else:
        return render_template("confirm.html", id=id, info=info, costs=costs, people=people, date=dateS, sameLocation=sameLocation(id), isPremium=info["isPremium"])