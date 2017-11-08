CREATE DATABASE moodtube;
USE moodtube;

CREATE TABLE Users(
	user_id VARCHAR(255) NOT NULL,
	twitter_username VARCHAR(255),
	twitter_api_key VARCHAR(255),
	CONSTRAINT users_pk PRIMARY KEY (user_id)
);

CREATE TABLE Likes(
	user_id VARCHAR(255) NOT NULL,
	gif_url VARCHAR(255) NOT NULL,
	CONSTRAINT likes_fk FOREIGN KEY (user_id) REFERENCES Users(user_id) 
);

CREATE TABLE Dislikes(
	user_id VARCHAR(255) NOT NULL,
	gif_url VARCHAR(255) NOT NULL,
	CONSTRAINT dislikes_fk FOREIGN KEY (user_id) REFERENCES Users(user_id)
);