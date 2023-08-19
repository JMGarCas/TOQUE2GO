from flask import render_template, request
from app import app
from helpers import login_required, checkUserInfo, db   
from constants import locations, allTypes

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

        location = request.form.get("location")
        if location != "default":
            if location not in locations:
                return render_template("explore.html", info=info, chefs=chefs, locations=locations, allTypes = allTypes, error="Invalid location")
            chefs = filter(lambda x: x['location'] == location, chefs)

        type = request.form.get("type")
        if type != "default":
            if type not in allTypes:
                return render_template("explore.html", info=info, chefs=chefs, locations=locations, allTypes = allTypes, error="Invalid type")
            chefs = filter(lambda chef: type in chef["types"], chefs)

        cost = request.form.get('cost')
        if not cost:
            cost = float('inf')
        if float(cost) <= 0.0:
            return render_template("explore.html", info=info, chefs=chefs, locations=locations, allTypes = allTypes, error="Invalid cost value")

        chefs = filter(lambda chef: chef["cost"] <= float(cost), chefs)

        return render_template("explore.html", info=info, chefs=list(chefs), locations=locations, allTypes = allTypes)
    else:
        return render_template("explore.html", info=info, chefs=chefs, locations=locations, allTypes = allTypes)