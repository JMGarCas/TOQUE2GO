from flask import redirect, session
from functools import wraps
from cs50 import SQL
from constants import DISCOUNT

db = SQL("sqlite:///toque.db")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

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

def sameLocation(id):
    currentUser = db.execute("SELECT location FROM users WHERE id = ?", session["user_id"])
    chef = db.execute("SELECT location FROM users WHERE id = ?", id)
    return currentUser == chef


def calculateCost(chef_id, people, cost):
    info = checkUserInfo()
    totalCost = 0
    discount = 0
    totalPricePerson = people * cost

    totalCost += totalPricePerson
    if not sameLocation(chef_id) and not info["isPremium"]:
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
