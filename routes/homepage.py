from helpers import checkUserInfo
from flask import render_template
from app import app

@app.route("/")
def homepage():
    """Shows to everyone the homepage"""
    info = checkUserInfo()
    return render_template("homepage.html", info=info)