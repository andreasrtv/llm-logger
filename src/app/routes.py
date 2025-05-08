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
    newest = db_utils.get_chats_for_user(current_user, newest=True)

    return (
        redirect(url_for("chats", chat_id=newest.id))
        if newest
        else redirect(url_for("new_chat"))
    )


@app.route("/chats/<chat_id>", methods=["GET", "POST"])
@login_required
def chats(chat_id):
    if request.method == "POST":
        data = db_utils.parse_bool_values(request.form.to_dict())

        try:
            db_utils.edit_chat(chat_id, **data)
        except ValueError as e:
            flash(str(e))

        if data.get("deleted"):
            db_utils.edit_user(current_user.id, option_show_completed=False)
            return redirect(url_for("home"))
        if data.get("completed"):
            db_utils.edit_user(current_user.id, option_show_completed=True)
            return redirect(url_for("home"))

        return redirect(url_for("chats", chat_id=chat_id))

    # GET
    chats_list = db_utils.get_chats_for_user(current_user)
    current_chat = next((c for c in chats_list if c.id == chat_id), None)

    if not current_chat:
        if current_user.option_show_completed:
            db_utils.edit_user(current_user.id, option_show_completed=False)
            return redirect(url_for("home"))
        return redirect(url_for("new_chat"))

    messages = []
    if current_chat.messages:
        msg_id = request.args.get("message_id")
        messages = (
            db_utils.get_branch_messages(msg_id)
            if msg_id and db_utils.get_branch_messages(msg_id)
            else db_utils.get_branch_messages(current_chat.messages[0].id)
        )

    all_tags = set(db_utils.get_tags())
    available_tags = sorted(
        all_tags - set(current_chat.tags), key=lambda t: t.text.lower()
    )

    return render_template(
        "chat.html",
        chats=chats_list,
        chat=current_chat,
        messages=messages,
        user=current_user,
        tags=available_tags,
    )


@app.route("/chats/new")
@login_required
def new_chat():
    chat_id = db_utils.create_chat(current_user.id)
    return redirect(url_for("chats", chat_id=chat_id))


@app.route("/users/me", methods=["POST"])
@login_required
def edit_user():
    raw_data = request.form.to_dict(flat=False)
    data = db_utils.parse_bool_values({k: v[-1] for k, v in raw_data.items()})

    user = db_utils.edit_user(current_user.id, **data)

    if user.option_show_completed:
        has_chats = (
            db_utils.get_chats(completed=True)
            if user.option_show_all
            else db_utils.get_chats(user_id=current_user.id, completed=True)
        )

        if not has_chats:
            db_utils.edit_user(current_user.id, option_show_completed=False)
            msg = (
                "No completed chats to show"
                if user.option_show_all
                else "No completed chats to show (for your user)"
            )
            flash(msg)

    return redirect(url_for("home"))


@app.route("/admin")
@login_required
def admin():
    return render_template(
        "admin.html",
        chats=db_utils.get_chats_for_user(current_user),
        user=current_user,
    )


@app.route("/admin/tags", methods=["POST"])
@login_required
def tags():
    text = request.form.get("text", "").strip()
    if text:
        try:
            db_utils.create_tag(text)
        except Exception as e:
            if "IntegrityError" in type(e).__qualname__:
                flash("Tag already exists")
    return redirect(url_for("home"))


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

        flash("Invalid credentials")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))
