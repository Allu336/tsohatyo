CREATE TABLE users (id SERIAL PRIMARY KEY, name TEXT, password TEXT, bio TEXT);
CREATE TABLE threads (id SERIAL PRIMARY KEY, title TEXT, time TIMESTAMP, user_id INTEGER REFERENCES users, topic TEXT, description TEXT);
CREATE TABLE privmessages (id SERIAL PRIMARY KEY, chat TEXT, text TEXT, user_id INTEGER REFERENCES users);
CREATE TABLE messages (id SERIAL PRIMARY KEY, time TIMESTAMP, thread_id INTEGER REFERENCES threads, user_id INTEGER REFERENCES users, text TEXT);
CREATE TABLE friends (id SERIAL PRIMARY KEY, user_id1 INTEGER REFERENCES users, user_id2 INTEGER REFERENCES users);
