ALTER TABLE Users ADD twitter_user_id VARCHAR(255);
ALTER TABLE Users DROP twitter_api_key;
CREATE TABLE Tokens(
    user_id INT4 NOT NULL,
    request_token VARCHAR(255),
    request_secret VARCHAR(255),
    oauth_token VARCHAR(255),
    oauth_token_secret VARCHAR(255),
    CONSTRAINT tokens_fk FOREIGN KEY (user_id) REFERENCES Users(user_id)
);
