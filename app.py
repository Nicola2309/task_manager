import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
#the difference here is that the installation uses the format "flask-pymongo" the import uses "flask_pymongo" and the packet is called "PyMongo"
from flask_pymongo import PyMongo
#MongDB stores data in a JSON-like format called BSON, to find documents we must be able to render/retrieve the ObjectId's.
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)


app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME") #This config command = GETS from env.py the database name
app.config["MONGO_URI"] = os.environ.get("MONGO_URI") #This config command = GETS from env.py the connection string
app.secret_key = os.environ.get("SECRET_KEY") #This secret_key command = GETS from env.py the required password to use functions from Flask

mongo = PyMongo(app) # la (app) passata come attributo e' : app = Flask(__name__)


@app.route("/")
@app.route("/get_tasks")
def get_tasks():
    # wrapping the find() mongodb method inside a Python list() changes the CURSOR OBJECT making it a proper LIST
    # That will solve the Jinja-repeatloops-bug explained in the 'tasks.html' page,
    tasks = list(mongo.db.tasks.find())
    #The light-blue 'tasks' is what the template will use, the white 'tasks' is the variable we defined in the line above.
    return render_template("tasks.html", tasks=tasks)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful")
        return redirect(url_for("profile", username=session["user"]))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if user exists in database
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            #ensure hashed password matches user input
            if check_password_hash(
                existing_user["password"], request.form.get("password")):
                    session["user"] = request.form.get("username").lower()
                    flash("Welcome, {}".format(
                        request.form.get("username")))
                    return redirect(url_for(
                        "profile", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))
        else:
            # user doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # grab the 'session' user's username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        #If the session user cookies are true and active show the profile of the user, if not, redirect him to the login page
        return render_template("profile.html", username=username)
    
    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    # remove user from session cookies
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/add_task", methods=["GET", "POST"])
def add_task():
    if request.method == "POST":
        is_urgent = "on" if request.form.get("is_urgent") else "off"
        task = {
            "category_name": request.form.get("category_name"),
            "task_name": request.form.get("task_name"),
            "task_description": request.form.get("task_description"), # If we want to retrieve an Array the correct method is 'request.form.getlist()'
            "is_urgent": is_urgent,
            "due_date": request.form.get("due_date"),
            "created_by": session["user"]
        }
        mongo.db.tasks.insert_one(task)
        flash("Task Successfully Added")
        return redirect(url_for("get_tasks"))

    categories = mongo.db.categories.find().sort("category_name", 1) # sorting categories by "1" displays them in numerical or alphabetical order
    return render_template("add_task.html", categories=categories)


@app.route("/edit_task/<task_id>", methods=["GET", "POST"])
def edit_task(task_id):
    if request.method == "POST":
        is_urgent = "on" if request.form.get("is_urgent") else "off"
        submit_edit = {
            "category_name": request.form.get("category_name"),
            "task_name": request.form.get("task_name"),
            "task_description": request.form.get("task_description"), # If we want to retrieve an Array the correct method is 'request.form.getlist()'
            "is_urgent": is_urgent,
            "due_date": request.form.get("due_date"),
            "created_by": session["user"]
        }
        mongo.db.tasks.update({"_id": ObjectId(task_id)},submit_edit)
        flash("Task Successfully Updated")

    task = mongo.db.tasks.find_one({"_id": ObjectId(task_id)})
    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("edit_task.html", task=task, categories=categories)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True) #debug value must be updated to FALSE prior to actual deployment or PROJECT SUBMISSION.
#If we open accidentally the APP in more than one terminal use "pkill -9 python3" to close the app everywhere.