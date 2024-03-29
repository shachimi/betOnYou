CREATE TABLE IF NOT EXISTS player (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(255) UNIQUE NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  first_name VARCHAR(255),
  last_name VARCHAR(255),
  is_active INT(11),
  game1_username VARCHAR(255) UNIQUE,
  game1_tag VARCHAR(255) UNIQUE,
  game2_username VARCHAR(255) UNIQUE,
  game2_tag VARCHAR(255) UNIQUE
);

CREATE TABLE IF NOT EXISTS clash_royale_stats (
  user_id INTEGER PRIMARY KEY NOT NULL,
  wins INTEGER,
  loses INTEGER,
  trophies INTEGER,
  FOREIGN KEY (user_id) REFERENCES player(id)
);

CREATE TABLE IF NOT EXISTS fortnite_stats (
  user_id INTEGER PRIMARY KEY NOT NULL,
  top1 INTEGER,
  kills INTEGER,
  matchesplayed INTEGER,
  FOREIGN KEY (user_id) REFERENCES player(id)
);
