CREATE DATABASE moodtube;
USE moodtube;

CREATE TABLE Users(
    user_id INT4 AUTO_INCREMENT NOT NULL,
    first_name varchar(255),
    last_name varchar(255),
    email varchar(255) UNIQUE,
    password varchar(255),
    twitter_username VARCHAR(255),
    twitter_user_id VARCHAR(255),
    CONSTRAINT users_pk PRIMARY KEY (user_id)
);

CREATE TABLE Likes(
    user_id INT4 NOT NULL,
    gif_url VARCHAR(255) NOT NULL,
    CONSTRAINT likes_fk FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

CREATE TABLE Dislikes(
    user_id INT4 NOT NULL,
    gif_url VARCHAR(255) NOT NULL,
    CONSTRAINT dislikes_fk FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

CREATE TABLE Tokens(
    user_id INT4 NOT NULL,
    request_token VARCHAR(255),
    request_secret VARCHAR(255),
    oauth_token VARCHAR(255),
    oauth_token_secret VARCHAR(255),
    CONSTRAINT tokens_fk FOREIGN KEY (user_id) REFERENCES Users(user_id)
);
