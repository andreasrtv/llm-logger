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
        form_data = {
            key: (
                value.lower() == "true" if value.lower() in ["true", "false"] else value
            )
            for key, value in request.form.to_dict().items()
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
            if len(current_chat.messages) != 0:
                message_id = request.args.get("message_id", None)

                if message_id:
                    messages = db_utils.get_branch_messages(message_id)

                if not message_id or messages == []:
                    messages = db_utils.get_branch_messages(current_chat.messages[0].id)
            else:
                messages = []

            return render_template(
                "chat.html",
                chats=chats,
                chat=current_chat,
                messages=messages,
                user=current_user,
                tags=sorted(
                    list(set(db_utils.get_tags()) - set(current_chat.tags)),
                    key=lambda t: t.text.lower(),
                ),
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
        key: (
            max(value).lower() == "true"
            if max(value).lower() in ["true", "false"]
            else max(value)
        )
        for key, value in request.form.to_dict(flat=False).items()
    }

    user = db_utils.edit_user(current_user.id, **form_data)

    if user.option_show_completed:
        if user.option_show_all:
            if not db_utils.get_all_chats(completed=True):
                db_utils.edit_user(current_user.id, option_show_completed=False)
                flash("No completed chats to show")
        else:
            if not db_utils.get_own_chats(current_user.id, completed=True):
                db_utils.edit_user(current_user.id, option_show_completed=False)
                flash("No completed chats to show (for your user)")

    return redirect(url_for("home"))


@app.route("/admin/tags", methods=["GET", "POST"])
@login_required
def tags():
    if request.method == "POST":
        text = request.form["text"]
        if text:
            try:
                db_utils.create_tag(text)
            except Exception as e:
                if type(e).__qualname__ == "IntegrityError":
                    flash("Tag already exists")
                    return redirect(url_for("admin"))

    return redirect(url_for("home"))


@app.route("/admin")
@login_required
def admin():
    if current_user.option_show_all:
        chats = db_utils.get_all_chats(completed=current_user.option_show_completed)
    else:
        chats = db_utils.get_own_chats(
            current_user.id, completed=current_user.option_show_completed
        )

    return render_template("admin.html", chats=chats, user=current_user)


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
