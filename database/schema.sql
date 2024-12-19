CREATE TABLE user (
    id SERIAL PRIMARY KEY,
    username VARCHAR(64) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL
);

CREATE TABLE recipe (
    id SERIAL PRIMARY KEY,
    title VARCHAR(140) NOT NULL,
    ingredients TEXT NOT NULL,
    instructions TEXT NOT NULL,
    image_url VARCHAR(200),
    category VARCHAR(64),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER REFERENCES user(id)
);

CREATE TABLE comment (
    id SERIAL PRIMARY KEY,
    comment_text TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    recipe_id INTEGER REFERENCES recipe(id),
    user_id INTEGER REFERENCES user(id)
);

CREATE TABLE rating (
    id SERIAL PRIMARY KEY,
    rating_value INTEGER NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    recipe_id INTEGER REFERENCES recipe(id),
    user_id INTEGER REFERENCES user(id)
);
