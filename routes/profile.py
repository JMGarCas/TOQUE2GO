from flask import render_template
from app import app
from helpers import login_required, checkUserInfo, reviewAlreadyWritten, getReviewsFromUser, getScore, db   

@app.route("/profile/<id>")
@login_required
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
        "location" : userInfo[0]["location"],
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