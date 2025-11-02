import uuid
import secrets
import bcrypt
import db.utils as db
import flask
from sess import r
from app import app
from otp import send_otp_email
from otp import generate
from otp import verify_otp


@app.post("/signup")
def signup():
    data = flask.request.get_json()

    name = data["name"]
    username = data["username"]
    email = data["email"]
    password = data["password"]
    role = data["password"] or None

    db.set_users(name, username, email, password, role)
    return flask.make_response(
        flask.jsonify({"status": "success", "message": "user signup successful!"}), 201
    )


@app.post("/login")
def login():
    data = flask.request.get_json()
    username = data["username"]
    email = data["email"] or None
    password = data["password"]

    user = db.get_user(username, email)
    if not user:
        return {"status": "not found", "message": "User not found"}, 404

    is_same_pw = bcrypt.checkpw(password.encode(), user["password"].encode())
    if not is_same_pw:
        return {"status": "error", "message": "Invalid password entered"}, 400

    ss_id = f"{uuid.uuid4()}|{user['role']}"
    r.setex(username, 3600, ss_id)

    return {
        "status": "success",
        "message": "Login successful",
        "session_id": ss_id,
    }


@app.route("/events", methods=["GET", "POST"])
def events():

    if flask.request.method == "POST":
        ss_id = flask.request.headers.get("Session-Id")
        data = flask.request.get_json()

        user = db.get_user(data["username"])
        if not user:
            return {"status": "Not found", "message": "User not found"}, 404

        if not ss_id:
            return {"status": "failure", "message": "No session id provided"}, 400

        stored_ss_id = r.get(data["username"])
        if not stored_ss_id:
            return {"status": "Not allowed", "message": "User is not logged In"}, 403

        if stored_ss_id != ss_id:
            return {"status": "failure", "message": "Invalid session id provided"}, 400

        title = data["title"]
        description = data["description"]
        event_date = data["event_date"]

        _, role = stored_ss_id.split(" ")
        if role != "admin":
            return (
                flask.make_response(
                    flask.jsonify(
                        {
                            "status": "Forbidden",
                            "message": "Not enough permissions to create an event",
                        }
                    )
                ),
                403,
            )

        db.create_event(title, description, event_date, user["user_id"])
        event = db.get_event(title=title)

        return {
            "status": "success",
            "message": "Successfully created an event",
            "event_id": event.get("event_id"),
        }

    events = db.get_events()

    if events:
        return {
            "status": "success",
            "message": "successfully retrieved all events",
            "events": events,
        }
    return {
        "status": "success",
        "message": "No events were retrieved",
        "events": events,
    }


@app.post("/register/<event_id>")
def register(event_id):
    event = db.get_event(event_id=event_id)
    data = flask.request.get_json()
    ss_id = flask.request.headers.get("Session-Id")
    username = data.get("username")

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
        return {"status": "failure", "message": "Invalid session id provided"}, 400

    registrations = db.get_registration()
    for registration in registrations:
        if event_id in registration and user.get("user_id") in registration:
            return {
                "status": "conflict",
                "message": "User has already registered for this event",
            }, 409

    db.insert_into_registrations(event_id, user.get("user_id"))


@app.post("confirm-attendance/<event_id>")
def confirm_attendace(event_id):
    data = flask.request.get_json()
    ss_id = flask.request.headers("Session-Id")
    otp = data["otp"]
    email = data["email"]
    user = db.get_user(email=email)

    if not ss_id:
        return {"status": "Failure", "message": "No session id provided"}, 400

    stored_ss_id = r.get(username)
    if stored_ss_id != ss_id:
        return {"status": "Failure", "message": "Invalid session id provided"}, 400

    event = db.get_event(event_id)
    if not event:
        return {"status": "failure", "message": "Event does not exist"}, 404

    if otp:
        if verify_otp(email, otp):
            db.update_registration_attendance(True, user.get("user_id"), event_id)
    else:
        username = data["username"]
        user_id = user.get("user_id")
        registered = db.get_registration()
        for r in registered:
            if user_id in r and event_id in r:
                otp = generate(email)
                send_otp_email(email)

        return {
            "status": "failure",
            "message": "User did no register for event",
        }, 404
