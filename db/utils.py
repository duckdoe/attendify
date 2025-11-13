import bcrypt
from .conn import connect_db

salt = bcrypt.gensalt()


def get_user(username=None, email=None):
    """
    A database utility function used to get a specific user by either their username or email


    :params: username:str | None
    :params: email: str | None

    :returns: A dictionary dict[str, Any]
    """

    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """
                SELECT * FROM users WHERE username=%s or email=%s
            """,
            (username, email),
        )
        user = cur.fetchone()

    if user:
        return {
            "user_id": user[0],
            "name": user[1],
            "username": user[2],
            "email": user[3],
            "password": user[4],
            "role": user[5],
            "created_at": user[6],
        }

    return None


def get_users(role=None, event_id=None):
    """
    A database utility function to get a user based on their role or event_id, this is used to see how much people have registered for an event

    if nothing is entered for both then no specifity will be added during search

    :params: role: str | None
    :params: event_id: UUID | None

    returns: list[dict[str, Any]]

    """
    if not role and not event_id:
        with connect_db() as conn:
            cur = conn.cursor()
            cur.execute("""SELECT * FROM users""")
            users = cur.fetchall()

    if role and event_id:
        with connect_db() as conn:
            cur = conn.cursor()
            cur.execute(
                """SELECT * FROM users WHERE role=%s and event_id=%s""",
                (role, event_id),
            )
            users = cur.fetchall()

    data = []
    if users:
        for user in users:
            data.append(
                {
                    "user_id": user[0],
                    "name": user[1],
                    "username": user[2],
                    "email": user[3],
                    "password": user[4],
                    "role": user[5],
                    "created_at": user[6],
                }
            )
    return data


def set_users(name, username, email, password, role=None):
    """
    A database utility function for creating users

    :params: name: str
    :params: username: str
    :params: email: str
    :params: password: str
    :params: role: str | None

    when the role is not specified or is given a falsy value the database defaults to 'user' for the role column

    returns
    None
    """

    hashed_pw = bcrypt.hashpw(password.encode(), salt).decode()

    if role:
        with connect_db() as conn:
            cur = conn.cursor()
            cur.execute(
                """INSERT INTO users(name, username, email, password, role) VALUES(%s,%s,%s,%s,%s)""",
                (name, username, email, hashed_pw, role),
            )
            conn.commit()
            return

    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO users (name, username, email, password) VALUES(%s,%s,%s,%s)""",
            (name, username, email, hashed_pw),
        )
        conn.commit()


def del_user(username):
    """
    A database utility function to delete/remove a user from the database

    :params: username: str

    returns None
    """
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute("""DELETE FROM users WHERE username=%s""", (username,))
        conn.commit()


def create_event(title, description, event_date, end_date, user_id):
    """
    A database utiliy function to create an event, events can only be created by admins

    :params: title: str
    :params: description: str
    :params: event_date: str
    :params: user_id: str

    The user_id and event_id parameters are needed for querying the database later

    returns None
    """
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO events (title, description, event_date, end_date, created_by) VALUES (%s, %s, %s, %s, %s)""",
            (title, description, event_date, end_date, user_id),
        )
        conn.commit()


def get_events():
    """
    A database utility function that returns all the events created over time

    This does not need any parameters as we need all the events created by different admins

    returns list[dict[str, Any]]
    """

    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute("""SELECT * FROM events""")
        events = cur.fetchall()

    data = []
    for event in events:
        event_id, title, description, event_date, created_by, created_at = event
        data.append(
            {
                "event_id": event_id,
                "title": title,
                "description": description,
                "event_date": event_date,
                "created_by": created_by,
                "created_at": created_at,
            }
        )
    return data


def get_event(title=None, event_id=None):
    """
    A database utility function that gets a certain event from the database either by the title or the event_id

    :params: title: str | None
    :params: event_id: str | None

    returns dict[str, Any]
    """
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """SELECT * FROM events WHERE title=%s or event_id=%s""", (title, event_id)
        )
        data = cur.fetchone()
    if data:
        event_id, title, description, event_date, created_by, created_at, end_date = (
            data
        )
        return {
            "event_id": event_id,
            "title": title,
            "description": description,
            "event_date": event_date,
            "end_date": end_date,
            "created_by": created_by,
            "created_at": created_at,
        }
    return None


def delete_event(event_id):
    """
    A database utility for deleting an event

    This can implemeted when the time for the event/program as ended and we dont need anything from it again

    :params: event_id: str | None

    returns None
    """

    with connect_db as conn:
        cur = conn.cursor()
        cur.execute("""DELETE FROM events WHERE event_id=%s""", (event_id,))
        conn.commit()


def get_registration():
    """
    A database utility used for getting the registered events of all users

    Again no need for parameters as we need everything

    returns None
    """

    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute("""SELECT * FROM registrations""")
        data = cur.fecthall()

    registrations = []

    if data:
        for d in data:
            registration_id, event_id, user_id, attended, registered_at = d
            registrations.append(
                {
                    "registration_id": registration_id,
                    "event_id": event_id,
                    "user_id": user_id,
                    "attended": attended,
                    "registered_at": registered_at,
                }
            )

    return registrations


# TODO Implement a way to get a specific event a user has registered for, possible params would be event_id and user_id


def get_registered(user_id, event_id):
    """
    A database utility function created to help with the retrival of a particular event a particular user is registered to

    :params: user_id: str
    :params: event_id: str

    returns dict[str, Any] | None
    """
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """
                    SELECT * FROM registrations WHERE event_id=%s AND user_id=%s
                    """,
            (event_id, user_id),
        )
        data = cur.fetchone()

    if data:
        reg_id, event_id, user_id, attended, registered_at = data
        return {
            "registration_id": reg_id,
            "event_id": event_id,
            "user_id": user_id,
            "attended": attended,
            "registered_at": registered_at,
        }
    return None


def get_single_registered(user_id=None, event_id=None):
    """
    A database utility function created to help with the retrival of a particular event a particular user is registered to

    :params: user_id: str
    :params: event_id: str

    returns dict[str, Any] | None
    """
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """
                    SELECT * FROM registrations WHERE event_id=%s OR user_id=%s
                    """,
            (event_id, user_id),
        )
        data = cur.fetchall()

    registered = []
    if data:
        for d in data:
            reg_id, event_id, user_id, attended, registered_at = d
            registered.append(
                {
                    "registration_id": reg_id,
                    "event_id": event_id,
                    "user_id": user_id,
                    "attended": attended,
                    "registered_at": registered_at,
                }
            )
        return registered

    return None


def insert_into_registrations(event_id, user_id):
    """
    A database utility function that is used to create/record events users register for

    :params: event_id: str
    :params: user_id
    """
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO registrations(event_id, user_id) VALUES(%s,%s)""",
            (event_id, user_id),
        )
        conn.commit()


def update_registration_attendance(attended, user_id, event_id):
    """
    A database utility function that is used to help mark the attendace of a user True

    :params: attended: bool
    :params: user_id: uuid
    :params: event_id: uuid
    """
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """UPDATE registrations SET attended=%s WHERE user_id=%s and event_id=%s""",
            (attended, user_id, event_id),
        )
        conn.commit()


def get_admins():
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute("""SELECT * FROM users WHERE role='admin'""")
        users = cur.fetchall()

    data = []
    if users:
        for user in users:
            data.append(
                {
                    "user_id": user[0],
                    "name": user[1],
                    "username": user[2],
                    "email": user[3],
                    "password": user[4],
                    "role": user[5],
                    "created_at": user[6],
                }
            )

    return data


def set_verification(user_id, event_id, document_url, image_url):
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO verification (user_id, event_id, document, image) VALUES (%s, %s, %s, %s)""",
            (user_id, event_id, document_url, image_url),
        )
        conn.commit()


def update_verification(id):
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """UPDATE verification SET approved=True WHERE verification_id=%s""", (id,)
        )
        conn.commit()


def add_points(points, user_id):
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """UPDATE users SET points= points + %s WHERE user_id=%s""",
            (points, user_id),
        )
        conn.commit()
