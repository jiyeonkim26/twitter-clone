#!/usr/bin/python3
"""
Add random users and messages to the existing Twitter Clone database.

This script:
- Keeps existing users
- Keeps existing messages
- Adds 200 new random users
- Adds 200 messages for each new user
- Adds 40,000 new messages total
"""

import argparse
import random
import sqlite3
from datetime import datetime, timedelta


parser = argparse.ArgumentParser(description="Add random data to the twitter project database")
parser.add_argument("--db_file", default="twitter_clone.db")
args = parser.parse_args()


NUM_USERS = 200
MESSAGES_PER_USER = 200


MESSAGE_STARTERS = [
    "Today I learned that",
    "I cannot believe that",
    "Just thinking about how",
    "Does anyone else think",
    "My hot take is that",
    "Currently working on",
    "I have been wondering if",
    "The best part of today was",
    "Honestly, I think",
    "Small update:",
]

MESSAGE_TOPICS = [
    "Python is actually pretty fun",
    "FastAPI makes web apps easier",
    "SQLite is helpful for small projects",
    "debugging takes longer than expected",
    "CSS is surprisingly powerful",
    "templates make websites more organized",
    "cookies are useful but confusing",
    "databases are starting to make sense",
    "HTML forms are kind of strange",
    "coding projects always teach you something new",
]

MESSAGE_ENDINGS = [
    "and I am still figuring it out.",
    "but it is finally starting to click.",
    "which feels like progress.",
    "and I think that is pretty interesting.",
    "even though it was confusing at first.",
    "and now I want to learn more.",
    "but I need more practice.",
    "so I am writing it down here.",
    "and that made my day better.",
    "which is why I like building things.",
]


def create_tables_if_needed(cur):
    """
    Creates the users and messages tables only if they do not already exist.
    This does not delete old data.
    """

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        age INTEGER
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL,
        message TEXT NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (sender_id) REFERENCES users(id)
    );
    """)


def random_message():
    """
    Creates one random message body.
    """

    starter = random.choice(MESSAGE_STARTERS)
    topic = random.choice(MESSAGE_TOPICS)
    ending = random.choice(MESSAGE_ENDINGS)

    return f"{starter} {topic}, {ending}"


def random_datetime():
    """
    Creates a random datetime within the last 60 days.
    Returns it as a string SQLite can store.
    """

    now = datetime.now()

    random_time = now - timedelta(
        days=random.randint(0, 60),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59),
    )

    return random_time.strftime("%Y-%m-%d %H:%M:%S")


def add_random_users(cur, num_users):
    """
    Adds new random users to the existing users table.
    Returns the ids of the newly created users.
    """

    first_names = [
        "alex", "jordan", "casey", "taylor", "morgan",
        "riley", "jamie", "avery", "quinn", "sam",
        "drew", "skylar", "devon", "charlie", "emerson"
    ]

    last_words = [
        "river", "coffee", "sunset", "reader", "runner",
        "garden", "cloud", "studio", "maple", "ocean",
        "field", "notebook", "pixel", "trail", "window"
    ]

    new_user_ids = []

    for _ in range(num_users):
        username = (
            random.choice(first_names)
            + "_"
            + random.choice(last_words)
            + str(random.randint(10, 9999))
        )

        password = "password"
        age = random.randint(18, 80)

        sql = """
        INSERT INTO users (username, password, age)
        VALUES (?, ?, ?);
        """

        try:
            cur.execute(sql, [username, password, age])
            new_user_ids.append(cur.lastrowid)

        except sqlite3.IntegrityError:
            # If this random username already exists, skip it.
            pass

    return new_user_ids


def add_random_messages(cur, user_ids, messages_per_user):
    """
    Adds random messages for each user id given.
    """

    total_messages = 0

    for user_id in user_ids:
        for _ in range(messages_per_user):
            message = random_message()
            created_at = random_datetime()

            sql = """
            INSERT INTO messages (sender_id, message, created_at)
            VALUES (?, ?, ?);
            """

            cur.execute(sql, [user_id, message, created_at])
            total_messages += 1

    return total_messages


def main():
    con = sqlite3.connect(args.db_file)
    cur = con.cursor()

    create_tables_if_needed(cur)

    new_user_ids = add_random_users(cur, NUM_USERS)
    total_messages = add_random_messages(cur, new_user_ids, MESSAGES_PER_USER)

    con.commit()
    con.close()

    print(f"Added {len(new_user_ids)} new users.")
    print(f"Added {total_messages} new messages.")
    print(f"Database updated: {args.db_file}")


if __name__ == "__main__":
    main()