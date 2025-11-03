import bcrypt
from .conn import connect_db

salt = bcrypt.gensalt()


def get_user(username=None, email=None):
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
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute("""DELETE FROM users WHERE username=%s""", (username,))
        conn.commit()


def create_event(title, description, event_date, user_id):
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO events (title, description, event_date, created_by) VALUES (%s, %s, %s,%s)""",
            (title, description, event_date, user_id),
        )
        conn.commit()


def get_events():
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
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """SELECT * FROM events WHERE title=%s or event_id=%s""", (title, event_id)
        )
        data = cur.fetchone()
    event_id, title, description, event_date, created_by, created_at = data
    return {
        "event_id": event_id,
        "title": title,
        "description": description,
        "event_date": event_date,
        "created_by": created_by,
        "created_at": created_at,
    }


def delete_events(event_id):
    with connect_db as conn:
        cur = conn.cursor()
        cur.execute("""DELETE FROM events WHERE event_id=%s""", (event_id,))
        conn.commit()


def get_registration():
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


def insert_into_registrations(event_id, user_id):
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO registrations(event_id, user_id) VALUES(%s,%s)""",
            (event_id, user_id),
        )
        conn.commit()


def update_registration_attendance(attended, user_id, event_id):
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """UPDATE registrations SET attended=%s WHERE user_id=%s and event_id=%s""",
            (attended, user_id, event_id),
        )
        conn.commit()
