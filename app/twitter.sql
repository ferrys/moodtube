ALTER TABLE Users ADD twitter_api_secret VARCHAR(255);
CREATE TABLE Tokens(
    request_token VARCHAR(255),
    request_secret VARCHAR(255)
);
