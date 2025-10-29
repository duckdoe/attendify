import os
from conn import connect_db

files = "migrations.txt"
dir = "schema/"


def get_migrated(files):
    with open(files) as f:
        contents = f.read()

    return contents.split(" ")


def get_files(dir):
    return os.listdir(dir)


a = get_migrated(files)
b = get_files(dir)


def migrate():
    migrated = False
    for file in b:
        if file not in a and file.endswith(".sql"):
            with open(files, "a") as f:
                f.write(f"{file} ")
            with open(os.path.join(dir, file)) as f:
                query = f.read()
            with connect_db() as conn:
                cur = conn.cursor()
                cur.execute(query)
                conn.commit()
            print(f". Migrated {file} successfully")

            migrated = True
    if not migrated:
        print("No files to migrate in 'db/schema/'")


if __name__ == "__main__":
    migrate()
