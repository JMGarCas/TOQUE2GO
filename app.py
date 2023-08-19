from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import date, datetime

from helpers import login_required

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///toque.db")

DISCOUNT = 0.05

ubications = [
    "Andalucía",
    "Aragón",
    "Asturias",
    "Cantabria",
    "Castilla-La Mancha",
    "Castilla y León",
    "Cataluña",
    "Extremadura",
    "Galicia",
    "Islas Baleares",
    "Islas Canarias",
    "La Rioja",
    "Madrid",
    "Murcia",
    "Navarra",
    "País Vasco",
    "Valencia",
]

allTypes = [
    "Mexican",
    "Spanish",
    "Italian",
    "Korean",
    "Japanese",
    "Chinese",
    "Thai",
    "Indian"
]

def checkUserInfo():
    info = {}
    if session:
        userInfo = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        info["id"] = session["user_id"]
        info["isPremium"] = userInfo[0]["membership"] == "premium"
        info["isAdmin"] = userInfo[0]["role"] == "admin"
        info["isChef"] = len(db.execute("SELECT id FROM users WHERE id = ? AND id IN (SELECT DISTINCT user_id FROM chefs)", session["user_id"])) != 0
    else:
        info["id"] = 0
        info["isPremium"] = False
        info["isAdmin"] = False
        info["isChef"] = False
    return info

def getReviewsFromUser(id):
    reviews = db.execute("SELECT * FROM reviews JOIN users ON reviews.writer_id == users.id WHERE reviews.user_id = ? ORDER BY reviews.date", id)
    try:
        reviews[0]
        return reviews
    except:
        return("No reviews")

def getScore(id):
    score = {
        "average" : db.execute("SELECT AVG(rating) FROM reviews JOIN users ON reviews.writer_id == users.id WHERE reviews.user_id = ?", id)[0]["AVG(rating)"],
        "number" :  db.execute("SELECT COUNT(rating) FROM reviews JOIN users ON reviews.writer_id == users.id WHERE reviews.user_id = ?", id)[0]["COUNT(rating)"]
    }
    return score

def reviewAlreadyWritten(id):
    reviews = db.execute("SELECT * FROM reviews JOIN users ON reviews.writer_id == users.id WHERE reviews.user_id = ? AND reviews.writer_id = ?", id, session["user_id"])
    try:
        reviews[0]
        return True
    except:
        return False

def appointmentAlreadyArranged(id, date):
    appointments = db.execute("SELECT * FROM appointments WHERE client_id = ? AND user_id = ? AND date = ?", session["user_id"], id, date)
    try:
        appointments[0]
        return True
    except:
        return False

def sameUbication(id):
    currentUser = db.execute("SELECT ubication FROM users WHERE id = ?", session["user_id"])
    chef = db.execute("SELECT ubication FROM users WHERE id = ?", id)
    return currentUser == chef


def calculateCost(chef_id, people, cost):
    info = checkUserInfo()
    totalCost = 0
    discount = 0
    totalPricePerson = people * cost

    totalCost += totalPricePerson
    if not sameUbication(chef_id) and not info["isPremium"]:
        totalCost += totalPricePerson

    if info["isPremium"]:
        discount = totalCost * DISCOUNT

    totalCost -= discount

    result = {
        "totalCost" : round(totalCost,2),
        "discount" : round(discount,2),
        "totalPricePerson" : round(totalPricePerson,2)
    }

    return result


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def homepage():
    """Shows to everyone the homepage"""
    info = checkUserInfo()
    return render_template("homepage.html", info=info)


@app.route("/explore", methods=["GET", "POST"])
@login_required
def explore():
    info = checkUserInfo()
    chefs = db.execute("SELECT * FROM users WHERE users.id IN (SELECT DISTINCT users.id FROM chefs JOIN users ON chefs.user_id == users.id)")
    for chef in chefs:
        try:
            chef["cost"]
        except:
            chef["cost"] = db.execute("SELECT DISTINCT cost FROM chefs WHERE chefs.user_id == ?", chef["id"])[0]["cost"]
        types = db.execute("SELECT type FROM chefs WHERE chefs.user_id == ?", chef["id"])
        types = map(lambda x:x["type"], types)
        chef["types"] = types

    if request.method == "POST":
        chefs = db.execute("SELECT * FROM users WHERE users.id IN (SELECT DISTINCT users.id FROM chefs JOIN users ON chefs.user_id == users.id)")
        for chef in chefs:
            try:
                chef["cost"]
            except:
                chef["cost"] = db.execute("SELECT DISTINCT cost FROM chefs WHERE chefs.user_id == ?", chef["id"])[0]["cost"]
            types = db.execute("SELECT type FROM chefs WHERE chefs.user_id == ?", chef["id"])
            types = list(map(lambda x:x["type"], types))
            chef["types"] = types

        ubication = request.form.get("ubication")
        if ubication != "default":
            if ubication not in ubications:
                return render_template("explore.html", info=info, chefs=chefs, ubications=ubications, allTypes = allTypes, error="Invalid ubication")
            chefs = filter(lambda x: x['ubication'] == ubication, chefs)

        type = request.form.get("type")
        if type != "default":
            if type not in allTypes:
                return render_template("explore.html", info=info, chefs=chefs, ubications=ubications, allTypes = allTypes, error="Invalid type")
            chefs = filter(lambda chef: type in chef["types"], chefs)

        cost = request.form.get('cost')
        if not cost:
            cost = float('inf')
        if float(cost) <= 0.0:
            return render_template("explore.html", info=info, chefs=chefs, ubications=ubications, allTypes = allTypes, error="Invalid cost value")

        chefs = filter(lambda chef: chef["cost"] <= float(cost), chefs)

        return render_template("explore.html", info=info, chefs=list(chefs), ubications=ubications, allTypes = allTypes)
    else:
        return render_template("explore.html", info=info, chefs=chefs, ubications=ubications, allTypes = allTypes)


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

        ubication = request.form.get("ubication")
        if ubication not in ubications:
            return render_template("register.html", error="Invalid ubication")

        hash = generate_password_hash(password)
        db.execute("INSERT INTO users (email, name, surname, hash, ubication, profile, banner) VALUES(?, ?, ?, ?, ?, ?, ?)", email, name, surname, hash, ubication, "/static/default-profile.png", "/static/default-banner.jpg")
        return redirect("/login")

    else:
        return render_template("register.html", ubications=ubications)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure email was submitted
        if not request.form.get("email"):
            return render_template("login.html", error="Must provide an email")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("login.html", error="Must provide a password")

        # Query database for email
        rows = db.execute(
            "SELECT * FROM users WHERE email = ?", request.form.get("email")
        )

        # Ensure email exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return render_template("login.html", error="Invalid email and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/profile/<id>")
def profile(id):
    info = checkUserInfo()
    isReviewAlreadyWritten = reviewAlreadyWritten(id)
    userInfo = db.execute("SELECT * FROM users WHERE id = ?", id)
    try:
        userInfo[0]
    except:
        return render_template("profile.html", info=info, isReviewAlreadyWritten=isReviewAlreadyWritten, error="User does not exist")

    profileInfo = {
        "id": userInfo[0]["id"],
        "name" : userInfo[0]["name"],
        "surname" : userInfo[0]["surname"],
        "ubication" : userInfo[0]["ubication"],
        "photo": userInfo[0]["profile"],
        "banner": userInfo[0]["banner"]
    }

    chefInfo = db.execute("SELECT * from users JOIN chefs ON users.id == chefs.user_id WHERE users.id == ?", id)
    try:
        chefInfo[0]
    except:
        return render_template("profile.html", info=info, isReviewAlreadyWritten=isReviewAlreadyWritten, profileInfo=profileInfo)

    types = map(lambda x:x["type"], chefInfo)
    chefInfo = {
        "information" : chefInfo[0]["information"],
        "cost" : chefInfo[0]["cost"],
        "types" : types
    }

    reviews = getReviewsFromUser(id)
    score = getScore(id)

    return render_template("profile.html", info=info, profileInfo=profileInfo, isReviewAlreadyWritten=isReviewAlreadyWritten, reviews=reviews, score=score, chefInfo=chefInfo)


@app.route("/edit-profile", methods=["GET", "POST"])
@login_required
def editprofile():
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
                    return render_template("edit-profile.html", info=info, isChef=isChef, error="Select distinct types of food", ubications=ubications)
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
        userCurrentUbication = userInfo[0]["ubication"]
        userCurrentProfile = userInfo[0]["profile"]
        userCurrentBanner = userInfo[0]["banner"]

        email = request.form.get("email")
        if len(db.execute("SELECT * FROM users WHERE email = ?", email)) != 0:
            return render_template("edit-profile.html", info=info, isChef=isChef, error="Email already registered", ubications=ubications)
        if email:
            userCurrentEmail = email
        name = request.form.get("name")
        if name:
            userCurrentName = name
        surname = request.form.get("surname")
        if surname:
            userCurrentSurname = surname
        ubication = request.form.get("ubication")
        if ubication not in ubications and ubication != "no-changes":
            return render_template("edit-profile.html", info=info, isChef=isChef, error="Invalid ubication", ubications=ubications)
        if ubication != "no-changes":
            userCurrentUbication = ubication
        profile = request.form.get("photo")
        if profile:
            userCurrentProfile = profile
        banner = request.form.get("banner")
        if banner:
            userCurrentBanner = banner

        db.execute("UPDATE users SET email = ?, name = ?, surname = ?, ubication = ?, profile = ?, banner = ? WHERE id = ?", userCurrentEmail, userCurrentName, userCurrentSurname, userCurrentUbication, userCurrentProfile, userCurrentBanner ,session["user_id"])

        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if password or confirmation:
            if not password:
                return render_template("edit-profile.html", info=info, isChef=isChef, error="Blank password", ubications=ubications)
            if not confirmation:
                return render_template("edit-profile.html", info=info, isChef=isChef, error="Blank confirmation", ubications=ubications)
            if not check_password_hash(
                userCurrentPassword, request.form.get("current")
            ):
                return render_template("edit-profile.html", info=info, isChef=isChef, error="Incorrect password", ubications=ubications)

            if confirmation != password:
                return render_template("edit-profile.html", info=info, isChef=isChef, error="New password not equal to confirmation", ubications=ubications)

            hash = generate_password_hash(password)
            db.execute("UPDATE users SET hash = ? WHERE id = ?", hash, session["user_id"])
            redirect("/logout")
            return redirect("/login")

        return redirect("/profile/"+str(session['user_id']))
    else:
        return render_template("edit-profile.html", info=info, isChef=isChef, ubications=ubications)


@app.route("/reviews/<id>", methods=["GET", "POST"])
@login_required
def reviews(id):
    info = checkUserInfo()
    sameUser = info["id"] == int(id)
    isReviewAlreadyWritten = reviewAlreadyWritten(id)
    isChef = True
    chefInfo = db.execute("SELECT * from chefs WHERE user_id == ?", id)
    try:
        chefInfo[0]
    except:
        isChef = False

    if isReviewAlreadyWritten:
        return render_template("reviews.html", id=id, info=info, isReviewAlreadyWritten=isReviewAlreadyWritten, sameUser=sameUser, isChef=isChef, error="You can not write another review on this profile")
    if sameUser:
        return render_template("reviews.html", id=id, info=info, isReviewAlreadyWritten=isReviewAlreadyWritten, sameUser=sameUser, isChef=isChef, error="You can not review your own profile")
    if not isChef:
        return render_template("reviews.html", id=id, info=info, isReviewAlreadyWritten=isReviewAlreadyWritten, sameUser=sameUser, isChef=isChef, error="You can only write a review to a chef")

    if request.method == "POST":
        rating = request.form.get("rating")
        if not rating or float(rating) <= 0.0 or float(rating) >= 5.0:
            return render_template("reviews.html", id=id, info=info,isReviewAlreadyWritten=isReviewAlreadyWritten, sameUser=sameUser, isChef=isChef, error="Invalid rating")
        text = request.form.get("text")
        if not text:
            return render_template("reviews.html", id=id, info=info, sameUser=sameUser, isChef=isChef, error="Blank text")
        db.execute("INSERT INTO reviews (writer_id, user_id, rating, text, date) VALUES (?, ?, ?, ?, ?)", info["id"], id, float(rating), text, date.today())
        return redirect("/profile/"+str(id))
    else:
        return render_template("reviews.html", id=id, info=info, isReviewAlreadyWritten=isReviewAlreadyWritten, sameUser=sameUser, isChef=isChef)


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


@app.route("/decline/<id>")
@login_required
def decline(id):
    info = checkUserInfo()
    appointment = db.execute("SELECT * FROM appointments WHERE id == ?", id)
    try:
        if appointment[0]["user_id"] != info["id"]:
            return render_template("appointments.html", info=info, error="You do not have permissions in this appointment")
        if appointment[0]["status"] == "waiting":
            db.execute("UPDATE appointments SET status = 'declined' WHERE id = ?", id)
            redirect("/appointments")
        else:
            return render_template("appointments.html", info=info, error="Appointment already accepted or declined")
    except:
        return render_template("appointments.html", info=info, error="Appointment with id "+str(id)+" does not exist")

    return redirect("/appointments")


@app.route("/arrange-appointment/<id>", methods=["GET", "POST"])
@login_required
def arrangeappointment(id):
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
        return render_template("confirm.html", id=id, info=info, costs=costs, people=people, date=dateS, sameUbication=sameUbication(id), isPremium=info["isPremium"])

@app.route("/users")
@login_required
def users():
    info = checkUserInfo()
    if info["isAdmin"]:
        users = db.execute("SELECT * FROM users")
        return render_template("users.html", id=id, info=info, users=users)
    else:
        return render_template("users.html", id=id, info=info, error="You do not have permissions here")

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
