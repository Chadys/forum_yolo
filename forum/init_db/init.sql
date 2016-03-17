PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS User;
CREATE TABLE User (
  id INTEGER PRIMARY KEY ASC,
  username VARCHAR(200) UNIQUE NOT NULL,
  email VARCHAR(300) UNIQUE NOT NULL,
  password VARCHAR(30) NOT NULL,
  nom VARCHAR(60),
  prenom VARCHAR(60),
  date_naiss DATE,
  date_creation REAL DEFAULT (datetime('now', 'localtime')),
  date_connection DATE
);

DROP TABLE IF EXISTS Topic;
CREATE TABLE Topic(
  id INTEGER PRIMARY KEY ASC,
  titre VARCHAR(500) NOT NULL,
  text TEXT,
  date_creation REAL DEFAULT (datetime('now', 'localtime')),
  date_modification REAL DEFAULT (datetime('now', 'localtime')),
  date_publication REAL,
  user_id INTEGER,
  sous_cat_id INTEGER NOT NULL,
  FOREIGN KEY(user_id) REFERENCES User(id) ON DELETE SET NULL ON UPDATE CASCADE,
  FOREIGN KEY (sous_cat_id) REFERENCES Sous_cat(id) ON DELETE CASCADE ON UPDATE CASCADE
);

DROP TABLE IF EXISTS Commentaire;
CREATE TABLE Commentaire(
  id INTEGER PRIMARY KEY ASC,
  titre VARCHAR(500),
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
  titre VARCHAR(500) UNIQUE NOT NULL,
  date_creation REAL DEFAULT (datetime('now', 'localtime')),
  date_modification REAL DEFAULT (datetime('now', 'localtime')),
  date_publication REAL
);

DROP TABLE IF EXISTS Sous_cat;
CREATE TABLE Sous_cat(
  id INTEGER PRIMARY KEY ASC,
  titre VARCHAR(500) NOT NULL,
  date_creation REAL DEFAULT (datetime('now', 'localtime')),
  date_modification REAL DEFAULT (datetime('now', 'localtime')),
  date_publication REAL,
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
  UPDATE Topic SET date_modification = (datetime('now', 'localtime')) WHERE Topic.id = NEW.id;
END;
CREATE TRIGGER after_update_commentaire AFTER UPDATE ON Commentaire FOR EACH ROW
BEGIN
  UPDATE Commentaire SET date_modification = (datetime('now', 'localtime')) WHERE Commentaire.id = NEW.id;
END;
CREATE TRIGGER after_update_categorie AFTER UPDATE ON Categorie FOR EACH ROW
BEGIN
  UPDATE Categorie SET date_modification = (datetime('now', 'localtime')) WHERE Categorie.id = NEW.id;
END;
CREATE TRIGGER after_update_sscat AFTER UPDATE ON Sous_cat FOR EACH ROW
BEGIN
  UPDATE Sous_cat SET date_modification = (datetime('now', 'localtime')) WHERE Sous_cat.id = NEW.id;
END;