PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS User;
CREATE TABLE User (
  id INTEGER PRIMARY KEY ASC,
  username VARCHAR(50) UNIQUE NOT NULL,
  email VARCHAR(300) UNIQUE NOT NULL,
  password VARCHAR(50) NOT NULL,
  nom VARCHAR(60),
  prenom VARCHAR(60),
  sexe VARCHAR(15),
  date_naiss DATE,
  date_creation REAL DEFAULT (datetime('now', 'localtime')),
  date_connection DATE DEFAULT (datetime('now', 'localtime')),
  permission TINYINT NOT NULL DEFAULT 7,
  FOREIGN KEY (permission) REFERENCES Permission(id) ON UPDATE CASCADE
);

DROP TABLE IF EXISTS Topic;
CREATE TABLE Topic(
  id INTEGER PRIMARY KEY ASC,
  titre VARCHAR(100) NOT NULL,
  text TEXT,
  date_creation REAL DEFAULT (datetime('now', 'localtime')),
  date_modification REAL DEFAULT (datetime('now', 'localtime')),
  date_publication REAL DEFAULT (datetime('now', 'localtime')),
  hidden BOOLEAN DEFAULT 0,
  user_id INTEGER,
  sous_cat_id INTEGER NOT NULL,
  FOREIGN KEY(user_id) REFERENCES User(id) ON DELETE SET NULL ON UPDATE CASCADE,
  FOREIGN KEY (sous_cat_id) REFERENCES Sous_cat(id) ON DELETE CASCADE ON UPDATE CASCADE
);

DROP TABLE IF EXISTS Commentaire;
CREATE TABLE Commentaire(
  id INTEGER PRIMARY KEY ASC,
  titre VARCHAR(100),
  text TEXT,
  date_creation REAL DEFAULT (datetime('now', 'localtime')),
  date_modification REAL DEFAULT (datetime('now', 'localtime')),
  user_id INTEGER,
  topic_id INTEGER NOT NULL,
  FOREIGN KEY (user_id) REFERENCES User(id) ON DELETE SET NULL ON UPDATE CASCADE,
  FOREIGN KEY (topic_id) REFERENCES Topic(id) ON DELETE CASCADE ON UPDATE CASCADE
);

DROP TABLE IF EXISTS Categorie;
CREATE TABLE Categorie(
  id INTEGER PRIMARY KEY ASC,
  titre VARCHAR(100) UNIQUE NOT NULL,
  date_creation REAL DEFAULT (datetime('now', 'localtime')),
  date_modification REAL DEFAULT (datetime('now', 'localtime')),
  date_publication REAL,
  hidden BOOLEAN DEFAULT 0
);

DROP TABLE IF EXISTS Sous_cat;
CREATE TABLE Sous_cat(
  id INTEGER PRIMARY KEY ASC,
  titre VARCHAR(100) NOT NULL,
  date_creation REAL DEFAULT (datetime('now', 'localtime')),
  date_modification REAL DEFAULT (datetime('now', 'localtime')),
  date_publication REAL,
  hidden BOOLEAN DEFAULT 0,
  categorie_id INTEGER NOT NULL,
  FOREIGN KEY (categorie_id) REFERENCES Categorie(id) ON DELETE CASCADE ON UPDATE CASCADE,
  UNIQUE (categorie_id,titre)
);

CREATE TRIGGER after_insert_commentaire AFTER INSERT ON Commentaire FOR EACH ROW
BEGIN
  UPDATE Topic SET date_publication = (datetime('now', 'localtime')) WHERE Topic.id = NEW.topic_id;
  
  UPDATE Sous_cat SET date_publication = (datetime('now', 'localtime')) WHERE Sous_cat.id = (
    SELECT sous_cat_id FROM Topic WHERE Topic.id = NEW.topic_id
  );
  
  UPDATE Categorie SET date_publication = (datetime('now', 'localtime')) WHERE Categorie.id = (
    SELECT categorie_id FROM Sous_cat WHERE Sous_cat.id = (
      SELECT sous_cat_id FROM Topic WHERE Topic.id = 1
    )
  );
END;

CREATE TRIGGER after_insert_topic AFTER INSERT ON Topic FOR EACH ROW
BEGIN
  UPDATE Sous_cat SET date_publication = (datetime('now', 'localtime')) WHERE Sous_cat.id = NEW.sous_cat_id;

  UPDATE Categorie SET date_publication = (datetime('now', 'localtime')) WHERE Categorie.id = (
    SELECT categorie_id FROM Sous_cat WHERE Sous_cat.id = NEW.sous_cat_id
  );
END;

CREATE TRIGGER after_update_topic AFTER UPDATE ON Topic FOR EACH ROW
BEGIN
  UPDATE Topic SET date_modification =
  CASE WHEN NEW.titre != OLD.titre OR NEW.text != OLD.text THEN
    (datetime('now', 'localtime'))
  ELSE
    date_modification
  END WHERE Topic.id = NEW.id;
END;
CREATE TRIGGER after_update_commentaire AFTER UPDATE ON Commentaire FOR EACH ROW
BEGIN
  UPDATE Commentaire SET date_modification = 
  CASE WHEN NEW.titre != OLD.titre OR NEW.text != OLD.text THEN
    (datetime('now', 'localtime'))
  ELSE
    date_modification
  END WHERE Commentaire.id = NEW.id;
END;
CREATE TRIGGER after_update_categorie AFTER UPDATE ON Categorie FOR EACH ROW
BEGIN
  UPDATE Categorie SET date_modification = 
  CASE WHEN NEW.titre != OLD.titre THEN
    (datetime('now', 'localtime'))
  ELSE
    date_modification
  END WHERE Categorie.id = NEW.id;
END;
CREATE TRIGGER after_update_sscat AFTER UPDATE ON Sous_cat FOR EACH ROW
BEGIN
  UPDATE Sous_cat SET date_modification = 
  CASE WHEN NEW.titre != OLD.titre THEN
    (datetime('now', 'localtime'))
  ELSE
    date_modification
  END WHERE Sous_cat.id = NEW.id;
END;


DROP TABLE IF EXISTS Permission;
CREATE TABLE Permission(
  id INTEGER PRIMARY KEY ASC,
  description VARCHAR(50) NOT NULL
);

INSERT INTO Permission (id,description) VALUES (0,'banned');
INSERT INTO Permission (description) VALUES
  ('see the connected navbar'),
  ('read what''s hidden'),
  ('edit one''s profile'),
  ('write com'),
  ('create topic'),
  ('edit/hide one''s com and topic'),
  ('view one''s edit history'),
  ('edit/hide other''s com and topic (including title)'),
  ('view other''s edit history'),
  ('ban/deban user'),
  ('edit other''s profile'),
  ('add/edit/delete/hide subcategory'),
  ('add/edit/delete/hide category'),
  ('ban/deban modo'),
  ('change user/modo permission');

INSERT INTO User (username,password,email,permission) VALUES ('admin','$2b$12$zcHw8a5AHKvmyeQgbspfG.JphhxzVaMfx.VdjOy9kG0.1I3Upo9Mi','iamyouradmin@haters.com',15);