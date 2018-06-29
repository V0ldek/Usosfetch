# Usosfetch
A Python script pushing email notifications for grade changes on USOSWeb.

Copyright (C) Mateusz Gienieczko 2018.
Licensed under GNU GPL.

A small Python script I wrote for automatization of USOSWeb checking for new grades.

## Configuration

The script is configured in two places. 

The first one is `config.ini`, which contains HTTP actions for 
logging in and out from the USOSWeb in the AUTHORIZATION group, and then course definitions in GRADES group.
A course definition is a key-value mapping, where the key is an alias for the courses name used in notifications,
and the value is a GET action yielding the grades page from USOSWeb (see images).

The second one is environment variables. The script expects the following environment variables (under `os.environ`):

- `USOS_USERNAME` - login for CAS authorization;
- `USOS_PASSWORD` - password for CAS authorization;
- `RECEIVER_EMAIL` - email to which the notifications will be sent;
- `NOTIFIER_USERNAME` - login to a notifier-bot GMail account;
- `NOTIFIER_PASSWORD` - password to a notifier-bot GMail account;
- `DATABASE_URL` - connection string to a PostgreSQL database.

## Database

The database has to accessible via psycopg2 (so PostgreSQL). The script expects a table with name Grades to exist,
with rows that have the fields:
- `ID` - corresponding to the course definition's key in `config.ini`;
- `List` - a CharacterString type that represents a JSON list of all grades in format mentioned below.

## Behaviour

The script is not exactly the smartest. It makes a lot of assumptions about the webpage it's used on
(since my intention wasn't really to use it for anything else than to satisfy my own laziness in checking the 
USOSWeb webpages for my grades). The script performs the following steps:

1. it logs in into USOSWeb via the `LOGIN_POST` action using credentials from the environment variables;
2. it fetches grades for all courses defined in `config.ini` in a form of a list;
3. it fetches the grades from the previous run of the script from the database;
4. it compares the lists for each course and lists all courses for which the lists differ;
5. it pushes a notification containing all differing courses (if it's not empty);
6. it stores the newly fetched grades in the database;
7. it logs out via the `LOGOUT_GET` action.

A sample USOSWeb grades page (the result of a POST specified in course definition) looks like this:

![example screenshot](https://github.com/V0ldek/Usosfetch/tree/master/images/exampleCourse.png "Example course grades GET.")


The script (again, not really smart) finds all objects with HTML tag `<td>` and takes data enclosed in tag `<b>` out of it,
since currently the GET returns a HTML file in which all actual points and grades satisfy this and only them. It then produces
a list, e.g.:
```json
[["1.0"], [], ["3.0"]]
```
which corresponds to three grade fields with the first and third one already filled with 1 and 3 points, respectively.

The email sent by the notifier contains all changed courses' IDs, like this:

![email screenshot](https://github.com/V0ldek/Usosfetch/tree/master/images/exampleEmail.png "Example email screenshot.")


## Usage

The script is meant to be ran continously, so it is recommended to host the script somewhere in the web and launch
it every 5-10 minutes to have up-to-date info about your grades. It also needs a PostreSQL database connected and
manually initialized with empty lists. The scripts execution time depends on connection delays to USOSWeb and the database,
and in practice it takes about 20-30 seconds to complete with 4 courses defined (the course GETs seem to take the most
time).
