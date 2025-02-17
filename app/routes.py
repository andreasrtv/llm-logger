from app import app, db_utils, login_manager
from flask import flash, redirect, render_template, request, send_file, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash


@login_manager.user_loader
def load_user(user_id):
    return db_utils.get_user_by(user_id=user_id)


@app.route("/")
@login_required
def home():
    if current_user.option_show_all:
        newest_chat = db_utils.get_newest_chat(
            completed=current_user.option_show_completed
        )
    else:
        newest_chat = db_utils.get_own_newest_chat(
            current_user.id, completed=current_user.option_show_completed
        )

    if newest_chat:
        return redirect(url_for("chats", chat_id=newest_chat.id))
    return redirect(url_for("new_chat"))


@app.route("/chats/<chat_id>", methods=["GET", "POST"])
@login_required
def chats(chat_id):
    if request.method == "POST":
        form_data = request.form.to_dict()

        form_data = {
            key: value for key, value in form_data.items() if value is not None
        }

        try:
            db_utils.edit_chat(chat_id, **form_data)
        except ValueError as e:
            flash(str(e))

        if "deleted" in form_data:
            db_utils.edit_user(current_user.id, option_show_completed=False)
            return redirect(url_for("home"))
        elif "completed" in form_data:
            db_utils.edit_user(current_user.id, option_show_completed=True)
            return redirect(url_for("home"))

        return redirect(url_for("chats", chat_id=chat_id))
    else:
        if current_user.option_show_all:
            chats = db_utils.get_all_chats(completed=current_user.option_show_completed)
        else:
            chats = db_utils.get_own_chats(
                current_user.id, completed=current_user.option_show_completed
            )

        current_chat = next((chat for chat in chats if chat.id == chat_id), None)

        if current_chat:
            messages = db_utils.get_messages(chat_id)

            return render_template(
                "chat.html",
                chats=chats,
                chat=current_chat,
                messages=messages,
                user=current_user,
            )
        elif not current_chat and current_user.option_show_completed:
            db_utils.edit_user(current_user.id, option_show_completed=False)
            return redirect(url_for("home"))
        else:
            return redirect(url_for("new_chat"))


@app.route("/chats/new")
@login_required
def new_chat():
    new_id = db_utils.create_chat(current_user.id)
    return redirect(url_for("chats", chat_id=new_id))


@app.route("/users/me", methods=["POST"])
@login_required
def edit_user():
    form_data = {
        key: max(values) for key, values in request.form.to_dict(flat=False).items()
    }

    form_data = {key: value for key, value in form_data.items() if value is not None}

    db_utils.edit_user(current_user.id, **form_data)

    if "option_show_completed" in form_data:
        if not db_utils.get_own_chats(
            current_user.id, completed=current_user.option_show_completed
        ):
            db_utils.edit_user(current_user.id, option_show_completed=False)
            flash("No completed chats to show")

    return redirect(url_for("home"))


@app.route("/admin")
@login_required
def admin():
    return render_template("admin.html", user=current_user)


@app.route("/admin/download")
@login_required
def download_db():
    path = app.config["SQLALCHEMY_DATABASE_URI"].split("://")[-1]
    return send_file(path_or_file=path)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if db_utils.get_user_by(username=username):
            flash("Username already exists")
            return redirect(url_for("register"))

        user = db_utils.create_user(username, password)

        login_user(user)
        return redirect(url_for("home"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = db_utils.get_user_by(username=username)
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for("home"))
        else:
            flash("Invalid credentials")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))
