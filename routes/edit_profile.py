from flask import session, request, render_template, redirect
from app import app
from helpers import login_required, checkUserInfo, db
from constants import allTypes, locations
from werkzeug.security import check_password_hash, generate_password_hash

@app.route("/edit-profile", methods=["GET", "POST"])
@login_required
def editProfile():
    info = checkUserInfo()
    isChef = True
    chefInfo = db.execute("SELECT * from chefs WHERE user_id == ?", session['user_id'])
    try:
        chefInfo[0]
    except:
        isChef = False

    if request.method == "POST":
        if isChef:
            types = request.form.getlist('type')
            userCurrentCost = chefInfo[0]["cost"]
            userCurrentInformation = chefInfo[0]["information"]

            cost = request.form.get("cost")
            if cost:
                userCurrentCost = cost
            information = request.form.get("information")
            if information:
                userCurrentInformation = information
            if len(types) > 0:
                if len(types) != len(set(types)):
                    return render_template("edit-profile.html", info=info, isChef=isChef, error="Select distinct types of food", locations=locations)
                userCurrentTypes = types
                db.execute("DELETE FROM chefs WHERE user_id = ?", session["user_id"])

                for type in userCurrentTypes:
                    if type in allTypes:
                        db.execute("INSERT INTO chefs (user_id, type, cost, information) VALUES (?, ?, ?, ?)", session["user_id"], type, float(userCurrentCost), userCurrentInformation)
            else:
                for i in chefInfo:
                    db.execute("UPDATE chefs SET cost = ?, information = ? WHERE user_id = ?", float(userCurrentCost), userCurrentInformation, session["user_id"])

        userInfo = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        userCurrentEmail = userInfo[0]["email"]
        userCurrentName = userInfo[0]["name"]
        userCurrentSurname = userInfo[0]["surname"]
        userCurrentPassword = userInfo[0]["hash"]
        userCurrentLocation = userInfo[0]["location"]
        userCurrentProfile = userInfo[0]["profile"]
        userCurrentBanner = userInfo[0]["banner"]

        email = request.form.get("email")
        if len(db.execute("SELECT * FROM users WHERE email = ?", email)) != 0:
            return render_template("edit-profile.html", info=info, isChef=isChef, error="Email already registered", locations=locations)
        if email:
            userCurrentEmail = email
        name = request.form.get("name")
        if name:
            userCurrentName = name
        surname = request.form.get("surname")
        if surname:
            userCurrentSurname = surname
        location = request.form.get("location")
        if location not in locations and location != "no-changes":
            return render_template("edit-profile.html", info=info, isChef=isChef, error="Invalid location", locations=locations)
        if location != "no-changes":
            userCurrentLocation = location
        profile = request.form.get("photo")
        if profile:
            userCurrentProfile = profile
        banner = request.form.get("banner")
        if banner:
            userCurrentBanner = banner

        db.execute("UPDATE users SET email = ?, name = ?, surname = ?, location = ?, profile = ?, banner = ? WHERE id = ?", userCurrentEmail, userCurrentName, userCurrentSurname, userCurrentLocation, userCurrentProfile, userCurrentBanner ,session["user_id"])

        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if password or confirmation:
            if not password:
                return render_template("edit-profile.html", info=info, isChef=isChef, error="Blank password", locations=locations)
            if not confirmation:
                return render_template("edit-profile.html", info=info, isChef=isChef, error="Blank confirmation", locations=locations)
            if not check_password_hash(
                userCurrentPassword, request.form.get("current")
            ):
                return render_template("edit-profile.html", info=info, isChef=isChef, error="Incorrect password", locations=locations)

            if confirmation != password:
                return render_template("edit-profile.html", info=info, isChef=isChef, error="New password not equal to confirmation", locations=locations)

            hash = generate_password_hash(password)
            db.execute("UPDATE users SET hash = ? WHERE id = ?", hash, session["user_id"])
            redirect("/logout")
            return redirect("/login")

        return redirect("/profile/"+str(session['user_id']))
    else:
        return render_template("edit-profile.html", info=info, isChef=isChef, locations=locations)