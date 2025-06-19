#===========================================================
# App Creation and Launch
#===========================================================

from flask import Flask, render_template, request, flash, redirect
import html

from app.helpers.session import init_session
from app.helpers.db import connect_db
from app.helpers.errors import register_error_handlers, not_found_error


# Create the app
app = Flask(__name__)

# Setup a session for messages, etc.
init_session(app)

# Handle 404 and 500 errors
register_error_handlers(app)


#-----------------------------------------------------------
# About page route
#-----------------------------------------------------------
@app.get("/about/")
def about():
    return render_template("pages/about.jinja")


#-----------------------------------------------------------
# Things page route - Show all the things, and new thing form
#-----------------------------------------------------------
@app.get("/")
def show_all_tasks():
    with connect_db() as client:
        # Get all the things from the DB
        sql = "SELECT priority, name, id, complete FROM tasks ORDER BY priority DESC"
        result = client.execute(sql)
        tasks = result.rows

        # And show them on the page
        return render_template("pages/home.jinja", tasks=tasks)


#-----------------------------------------------------------
# Thing page route - Show details of a single thing
#-----------------------------------------------------------
@app.get("/task/<int:id>")
def show_one_task(id):
    with connect_db() as client:
        # Get the thing details from the DB
        sql = "SELECT id, name, priority, complete FROM tasks WHERE id=?"
        values = [id]
        result = client.execute(sql, values)

        # Did we get a result?
        if result.rows:
            # yes, so show it on the page
            task = result.rows[0]
            return render_template("pages/task.jinja", task=task)

        else:
            # No, so show error
            return not_found_error()


#-----------------------------------------------------------
# Route for adding a thing, using data posted from a form
#-----------------------------------------------------------
@app.post("/add")
def add_a_task():
    # Get the data from the form
    task  = request.form.get("task")
    priority = request.form.get("priority")

    # Sanitise the inputs
    task = html.escape(task)
    priority = html.escape(priority)

    with connect_db() as client:
        # Add the thing to the DB
        sql = "INSERT INTO tasks (name, priority) VALUES (?, ?)"
        values = [task, priority]
        client.execute(sql, values)

        # Go back to the home page
        flash(f"Task '{task}' added", "success")
        return redirect("/")


#-----------------------------------------------------------
# Route for deleting a thing, Id given in the route
#-----------------------------------------------------------
@app.get("/delete/<int:id>")
def delete_a_task(id):
    with connect_db() as client:
        # Delete the thing from the DB
        sql = "DELETE FROM tasks WHERE id=?"
        values = [id]
        client.execute(sql, values)

        # Go back to the home page
        return redirect("/")

# #-----------------------------------------------------------
# # A complete task
# #-----------------------------------------------------------
@app.get("/complete/<int:id>")
def complete_task(id):
    with connect_db() as client:
        sql = "UPDATE tasks set complete=? WHERE=?"
        values = [1, id]
        client.execute(sql, values)
        return redirect("/")
    
# #-----------------------------------------------------------
# # A incomplete task
# #-----------------------------------------------------------
@app.get("/incomplete/<int:id>")
def incomplete_task(id):
    with connect_db() as client:
        sql = "UPDATE tasks set complete=? WHERE=?"
        values = [0, id]
        client.execute(sql, values)
        return redirect("/")