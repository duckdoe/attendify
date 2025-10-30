import uuid
from sess import r
import bcrypt
import db.utils as db
import flask
from app import app


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

        db.create_event(title, description, event_date, user["user_id"])

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
