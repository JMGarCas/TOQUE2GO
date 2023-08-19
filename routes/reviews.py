from flask import request, render_template, redirect
from app import app
from helpers import login_required, checkUserInfo, reviewAlreadyWritten, db
from datetime import date

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
