CREATE TABLE player (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username VARCHAR(255) UNIQUE NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  first_name VARCHAR(255),
  last_name VARCHAR(255),
  is_active INT(11),
  game1_username VARCHAR(255) UNIQUE,
  game2_username VARCHAR(255) UNIQUE
);
