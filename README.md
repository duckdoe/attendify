# Attendify

A attendance tracker application that allows admins to create events and for users to register for events and confirm their attendance

### Features
- Signup and login
- Creating events (only admins)
- Registering for events (admins and users)
- Otp verification
- Uploading of files event attendance verification

### For developers

To start development run the following commands on your desired terminal

| Clone this repository:

``bash``
```
git clone https://github.com/duckdoe/attendify
```

| Install the packages needed to run the app

``bash``
```
cd  attendify

python -m venv venv

source venv/Scripts/activate

pip install
```



To create the db go into go into th db folder look for the conn.py file and edit the contents to match your database configuration. To create the tables cd into your root folder and run the following commands on the terminal of your choice.

``bash``
```
cd db
python migrate.py
```

This will create the tables in the db you specified in conn.py

Now run the flask server by doing this, go tho the root directory and run
``bash``

```
python run.py
```