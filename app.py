import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
# the difference here is that the installation uses the format "flask-pymongo" the import uses "flask_pymongo" and the packet is called "PyMongo"
from flask_pymongo import PyMongo
# MongDB stores data in a JSON-like format called BSON, to find documents we must be able to render/retrieve the ObjectId's.
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)


app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME") # This config command = GETS from env.py the database name
app.config["MONGO_URI"] = os.environ.get("MONGO_URI") # This config command = GETS from env.py the connection string
app.secret_key = os.environ.get("SECRET_KEY") # This secret_key command = GETS from env.py the required password to use functions from Flask

mongo = PyMongo(app) # la (app) passata come attributo e' : app = Flask(__name__)
                     # se vogliamo aprire il 'Search Index' nella CLI, dopo aver avviato l'interprete python con il comando 'python3', sara' il comando 'from app import mongo' ad avviare la connessione tra Database, Python e App.
                     # 'mongo.db.tasks.create_index([("task_name", "text"), ("task_descrption", "text")])' possiamo avere solo un 'Text Index' per collection, questo lo mettiamo con le tasks. I nostri user potranno ricercare le tasks in base al loro nome o descrizione
                     # 'mongo.db.tasks.drop_indexes()' per rimuovere gli indici di ricerca
                     # 'mongo.db.tasks.drop_index('task_name_text_task_descrption_text')' per rimuovore l'indice di ricerca creato col comando scritto sopra
                     # 'mongo.db.tasks.index_information()' per vedere la logica di indicizzazione presente, quella di default in mongoDB e' il numero crescente degli ID:  {'_id_': {'v': 2, 'key': [('_id', 1)], 'ns': 'task_manager.tasks'}}


@app.route("/")
@app.route("/get_tasks")
def get_tasks():
    # wrapping the find() mongodb method inside a Python list() changes the CURSOR OBJECT making it a proper LIST
    # That will solve the Jinja-repeatloops-bug explained in the 'tasks.html' page,
    tasks = list(mongo.db.tasks.find())
    # The light-blue 'tasks' is what the template will use, the white 'tasks' is the variable we defined in the line above.
    return render_template("tasks.html", tasks=tasks)


@app.route("/search", methods=["GET", "POST"])
# creare l'indice con python permette a tutti gli user di usare la ricerca contemporaneamente, 
# se la creassimo interna all'app crusherebbe aggiungendo nella funzione 'def.search()' 'mongo.db.tasks.create_index([("task_name", "text"), ("task_description", "text")])' le queries si legherebbero alla sessione del singolo user, e con due in contemporanea crusherebbe.
# Check STOP words Docs of Mongo
def search():
    query = request.form.get("query")
    tasks = list(mongo.db.tasks.find({"$text": {"$search": query}}))
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
            # ensure hashed password matches user input
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
        # If the session user cookies are true and active show the profile of the user, if not, redirect him to the login page
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
        mongo.db.tasks.update({"_id": ObjectId(task_id)}, submit_edit)
        flash("Task Successfully Updated")
        return redirect(url_for("get_tasks"))

    task = mongo.db.tasks.find_one({"_id": ObjectId(task_id)})
    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("edit_task.html", task=task, categories=categories)


@app.route("/delete_task/<task_id>")
def delete_task(task_id):
    mongo.db.tasks.remove({"_id": ObjectId(task_id)})
    flash("Task Successfully Deleted")
    return redirect(url_for("get_tasks"))


@app.route("/get_categories")
def get_categories():
    categories = list(mongo.db.categories.find().sort("category_name", 1))
    return render_template("categories.html", categories=categories)


@app.route("/add_category", methods=["GET", "POST"])
def add_category():
    if request.method == "POST":
        category = {
            "category_name": request.form.get("category_name")
        }
        mongo.db.categories.insert_one(category)
        flash("New Category Added")
        return redirect(url_for("get_categories"))

    return render_template("add_category.html")


@app.route("/edit_category/<category_id>", methods=["GET", "POST"])
def edit_category(category_id):
    if request.method == "POST":
        submit = {
            "category_name": request.form.get("category_name")
        }
        mongo.db.categories.update({"_id": ObjectId(category_id)}, submit)
        flash("Category Successfully Updated")
        return redirect(url_for("get_categories"))

    category = mongo.db.categories.find_one({"_id": ObjectId(category_id)})
    return render_template("edit_category.html", category=category)


@app.route("/delete_category/<category_id>")
def delete_category(category_id):
    mongo.db.categories.remove({"_id": ObjectId(category_id)})
    flash("Category Successfully Deleted")
    return redirect(url_for("get_categories"))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True) # debug value must be updated to FALSE prior to actual deployment or PROJECT SUBMISSION.
# If we open accidentally the APP in more than one terminal use "pkill -9 python3" to close the app everywhere.