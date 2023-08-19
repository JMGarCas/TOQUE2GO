from cs50 import SQL
from flask import Flask
from flask_session import Session

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///toque.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

import routes.homepage
import routes.explore
import routes.chef
import routes.register
import routes.login
import routes.logout
import routes.profile
import routes.edit_profile
import routes.reviews
import routes.appointments
import routes.accept
import routes.decline
import routes.arrange_appointment
import routes.confirm
import routes.users
import routes.delete
import routes.premium