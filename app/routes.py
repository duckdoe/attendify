import os
import uuid
import bcrypt
import db.utils as db
import flask
from datetime import datetime
from werkzeug.utils import secure_filename
from .sess import r
from app import app
from .otp import send_otp_email
from .otp import generate
from .otp import verify_otp
from .otp import send_login_alert
from .otp import send_registration_email


app.config["UPLOADS_FOLDER"] = "app\\uploads"
app.config["ALLOWED_FILES"] = ["docx", "pdf", "png", "jpg", "jpeg"]


@app.post("/signup")
def signup():
    """
    Signup route for app

    receives data from the client such as

    :name: str

    :username: str

    :email: str

    :password: str

    :role: str | None

    if role is not giving or is a falsy value the database function will handle that
    """

    data = flask.request.get_json()

    name = data.get("name")
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role")

    if not all([name, username, email, password]):
        return {"status": "failure", "message": "Missing field in payload"}, 400

    db.set_users(name, username, email, password, role)
    return {"status": "success", "message": "user signup successful!"}, 201


@app.post("/login")
def login():
    """
    A login route for the app

    Recieves data from the client

    :returns: randomly generated session id
    """
    data = flask.request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not all(
        [
            username,
            username or email,
            password,
        ]
    ):
        return {"message": "Missing field in payload"}, 400

    user = db.get_user(username, email)
    if not user:
        return {
            "status": "not found",
            "message": "User not found or does not eixst",
        }, 404

    is_same_pw = bcrypt.checkpw(password.encode(), user["password"].encode())
    if not is_same_pw:
        return {"status": "error", "message": "Invalid password entered"}, 400

    ss_id = f"{uuid.uuid4()}|{user['role']}"
    try:
        r.setex(user["username"], 3600, ss_id)
    except ConnectionError:
        return {
            "message": "Network error, make sure you have a stable internet connectioon and try again"
        }, 400
    except TimeoutError:
        return (
            {"message": "Recieved a timeout error while trying to connect to redis"},
        )

    ip = flask.request.remote_addr
    send_login_alert(email or user.get("email"), ip)

    return {
        "status": "success",
        "message": "Login successful",
        "session_id": ss_id,
    }


@app.route("/events", methods=["GET", "POST"])
def events():
    """
    The events api of the route

    This route accepts both a post and get request

    The POST request is used for creating a new event

    :restrictions: only admins can create events

    The GET request is used for retereiving all the events created
    """

    if flask.request.method == "POST":
        ss_id = flask.request.headers.get("Session-Id")
        data = flask.request.get_json()

        username = data.get("username")
        if not username:
            return {"Missing field in payload"}, 400

        user = db.get_user(username)
        if not user:
            return {
                "status": "Not found",
                "message": "User not found or does not exist",
            }, 404

        if not ss_id:
            return {
                "status": "failure",
                "message": "No session id provided failed to authenticate",
            }, 400

        stored_ss_id = r.get(data["username"])
        if not stored_ss_id:
            return {"status": "Not allowed", "message": "Session Id has expired"}, 403

        if stored_ss_id != ss_id:
            return {
                "status": "failure",
                "message": "Invalid session id provided failed to authenticate",
            }, 400

        title = data.get("title")
        description = data.get("description")
        event_date = data.get("event_date")
        end_date = data.get("end_date")

        if not all([title, description, event_date]):
            return {"message": "Missing field in payload"}, 400

        _, role = stored_ss_id.split("|")
        if role != "admin":
            return {
                "status": "Forbidden",
                "message": "Not enough permissions to create an event, need admin priviledges",
            }, 403

        db.create_event(title, description, event_date, end_date, user["user_id"])
        event = db.get_event(title=title)

        return {
            "status": "success",
            "message": "Event created succesffully",
            "event_id": event.get("event_id"),
        }, 201

    events = db.get_events()

    if events:
        return {
            "status": "success",
            "message": "Event created successfully",
            "events": events,
        }

    return {
        "status": "success",
        "message": "No events were retrieved, try creating one?",
    }


@app.post("/register/<event_id>")
def register(event_id):
    """
    This route is used to register a user for an event
    """

    event = db.get_event(event_id=event_id)
    data = flask.request.get_json()
    ss_id = flask.request.headers.get("Session-Id")
    username = data.get("username")

    if not username:
        return {"message": "Missing field in payload"}, 400

    user = db.get_user(username)

    if not event:
        return {"status": "Not found", "message": "Event not found"}, 404
    if not ss_id:
        return {
            "status": "Failure",
            "message": "No session id provided failed to authenticate",
        }, 400

    stored_ss_id = r.get(username)
    if stored_ss_id != ss_id:
        return {
            "status": "failure",
            "message": "Invalid session id provided failed to authenticate",
        }, 400

    registered = db.get_registered(user_id=user["user_id"], event_id=event_id)
    if registered:
        return {
            "status": "conflict",
            "message": "User has already registered for this event",
        }, 409

    db.insert_into_registrations(event_id, user.get("user_id"))

    admins = db.get_admins()
    for admin in admins:
        send_registration_email(
            admin["email"],
            username,
            event["title"],
        )
    return {"status": "success", "message": "User registered for event successful"}, 201


@app.get("/event")
def event():
    ss_id = flask.request.headers.get("Session-Id")
    event_id = flask.request.args.get("event_id")
    username = flask.request.args.get("username")

    user = db.get_user(username)

    if not user:
        return {"status": "Not found", "message": "User not found"}, 404

    stored_ss_id = r.get(username)
    if stored_ss_id != ss_id:
        return {"status": "error", "message": "Invalid session id provided"}, 400

    user_id = user.get("user_id")
    if username and not event_id:
        registrations = db.get_single_registered(user_id=user_id)
        return {
            "status": "success",
            "message": "successfully retrived user events",
            "events": registrations,
        }, 200

    if username and event_id:
        _, role = stored_ss_id.split("|")
        if role != "admin":
            return {
                "status": "Forbidden",
                "message": "Not enough permissions to perform this action need admin privileges",
            }, 405
        registrations = db.get_single_registered(event_id=event_id)
        return {
            "status": "success",
            "message": "successfully retrived user events",
            "events": registrations,
        }, 200
    return {"status": "error", "message": "No search parameter provided"}, 400


@app.put("/confirm-attendance/<event_id>/verify-otp")
def verify_otp_route(event_id):
    """
    This route is used to confirm the otp provided by the user

    :params: event_id: str
    """
    data = flask.request.get_json()
    ss_id = flask.request.headers.get("Session-Id")
    email = data.get("email")
    otp = data.get("otp")
    user = db.get_user(email=email)

    if not all(email, otp):
        return {"message": "Missing field in payload"}, 400

    username = user.get("username")

    if not ss_id:
        return {
            "status": "Failure",
            "message": "No session id provided failed to authenticate",
        }, 400

    stored_ss_id = r.get(username)
    if stored_ss_id != ss_id:
        return {
            "status": "Failure",
            "message": "Invalid session id provided failed to authenticate",
        }, 400

    event = db.get_event(event_id=event_id)
    if not event:
        return {"status": "failure", "message": "Event does not exist"}, 404

    if not otp:
        return {"status": "failure", "message": "No otp provided"}, 400

    if verify_otp(email, otp):
        db.update_registration_attendance(
            attended=True, user_id=user.get("user_id"), event_id=event_id
        )

        current_time = datetime.now()

        def get_points(current_time, start_time, end_time):

            if (
                (type(current_time) != datetime)
                and type(start_time) != datetime
                and type(end_time) != datetime
            ):
                raise TypeError("Invalid object provided need a datetime object")

            total_time = int((start_time - end_time).total_seconds())
            remaining_time = int((current_time - end_time).total_seconds())

            points = remaining_time // total_time * 10
            return points

        points = get_points(current_time, event.get("event_date", "end_date"))
        db.add_points(points, user.get("user_id"))

        return {
            "status": "success",
            "message": "Otp verification successful attendance updated",
            "points": f"{points} where added",
        }, 200
    else:
        return {
            "status": "failure",
            "message": "Invalid otp provided or otp has expired",
        }, 400


@app.post("/confirm-attendance/<event_id>")
def confirm_attendace(event_id):
    """
    This route is used to confirm the attendance of an event

    :params: event_id: str
    """
    data = flask.request.get_json()
    ss_id = flask.request.headers.get("Session-Id")
    email = data.get("email")
    user = db.get_user(email=email)

    if not email:
        return {"message": "Missing field in payload"}, 400

    username = user["username"]

    if not ss_id:
        return {
            "status": "Failure",
            "message": "No session id provided failed to authenticate",
        }, 400

    stored_ss_id = r.get(username)
    if stored_ss_id != ss_id:
        return {
            "status": "Failure",
            "message": "Invalid session id provided failed to authenticate",
        }, 400

    event = db.get_event(event_id=event_id)
    if not event:
        return {"status": "failure", "message": "Event does not exist"}, 404

    user_id = user.get("user_id")
    registered = db.get_registered(user_id, event_id)

    current_time = datetime.now()
    if current_time > event.get("end_date"):
        return {
            "message": "Event has already ended you need proof to confirm your attendance"
        }, 409

    if registered:
        otp = generate(email)
        send_otp_email(email, otp)
        return {
            "status": "success",
            "message": "Otp sent to provided email",
        }, 200

    return {
        "status": "failure",
        "message": "User did not register for event",
    }, 404


@app.post("/confirm-attendance/<event_id>/upload")
def verify_attendance(event_id):
    ss_id = flask.request.headers.get("Session-Id")
    email = flask.request.form.get("email")
    user = db.get_user(email=email)

    if not email:
        return {"message": "Missing field in payload"}, 400

    username = user["username"]

    if not ss_id:
        return {
            "status": "Failure",
            "message": "No session id provided failed to authenticate",
        }, 400

    stored_ss_id = r.get(username)
    if stored_ss_id != ss_id:
        return {
            "status": "Failure",
            "message": "Invalid session id provided failed to authenticate",
        }, 400

    event = db.get_event(event_id=event_id)
    if not event:
        return {"status": "failure", "message": "Event does not exist"}, 404

    if flask.request.files:
        if "document" not in flask.request.files and "image" not in flask.request.files:
            return {"message": "Missing requirements"}, 400

        document = flask.request.files["document"]
        image = flask.request.files["image"]

        if document.filename == "" or image.filename == "":
            return {"error": "No selected file"}, 400

        files = []

        if document.filename.endswith(tuple(app.config["ALLOWED_FILES"])):
            filename = secure_filename(document.filename)

            full_path = os.path.join(
                os.getcwd(),
                app.config["UPLOADS_FOLDER"],
                "documents",
                filename,
            )
            document.save(full_path)

            file_url = flask.url_for("uploaded_file", filename=filename, _external=True)
            files.append(file_url)

        if image.filename.endswith(tuple(app.config["ALLOWED_FILES"])):
            filename = secure_filename(image.filename)

            full_path = os.path.join(
                os.getcwd(),
                app.config["UPLOADS_FOLDER"],
                "images",
                filename,
            )
            image.save(full_path)

            file_url = flask.url_for("uploaded_file", filename=filename, _external=True)
            files.append(file_url)

        document_url, image_url = files
        db.set_verification(
            user.get("user_id"), event.get("event_id"), document_url, image_url
        )
        return {"message": "Images sent verification is ongoing"}, 201


@app.route("/uploaded_file/<filename>")
def uploaded_file(filename):
    if filename.endswith(".png") or filename.endswith(".jpeg"):
        return flask.send_from_directory("uploads\\images", filename)

    if filename.endswith(".docx") or filename.endswith(".pdf"):
        return flask.send_from_directory("uploads\\documents", filename)
