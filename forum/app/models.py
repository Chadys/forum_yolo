# coding=utf-8
from __future__ import absolute_import
import sqlite3
from flask import g


def connect_db():
    return sqlite3.connect('forum.db')


def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db



class User(object):
    """
    Class permettant de manipuler la table User
    """
    @classmethod
    def insert(cls, username, password, email):
        db = get_db()
        try:
            db.execute("""INSERT INTO User (username, password, email) VALUES (?, ? ,?)""", [username, password, email])
            db.commit()
        except sqlite3.IntegrityError as e:
            print "Insert error for {user} : {message}".format(user=username, message=e.message)

    @classmethod
    def get_user_id(cls, id):
        db = get_db()
        cur = db.execute("""SELECT id, username, email, date_creation, date_connection, nom, prenom, date_naiss FROM User WHERE id=?""", [id])
        result = cur.fetchone()
        if result:
            result = {
                'id': result[0],
                'username': result[1],
                'email': result[2],
                'date_creation': result[3],
                'date_connection': result[4],
                'nom': result[5]
,                'prenom': result[6],
                'date_naiss': result[7]
            }
        return result

    @classmethod
    def get_user(cls, username):
        db = get_db()
        cur = db.execute("""SELECT id, username, email, date_creation, date_connection, nom, prenom, date_naiss  FROM User WHERE username=?""", [username])
        result = cur.fetchone()
        if result:
            result = {
                'id': result[0],
                'username': result[1],
                'email': result[2],
                'date_creation': result[3],
                'date_connection': result[4],
                'nom': result[5],
                'prenom': result[6],
                'date_naiss': result[7]
            }
        return result

    @classmethod
    def get_topics(cls, id):
        db = get_db()
        cur = db.execute("""SELECT Topic.id, Topic.titre, Topic.sous_cat_id, COUNT(Commentaire.id) AS nb_com FROM Topic LEFT JOIN Commentaire ON Topic.id = Commentaire.topic_id WHERE Topic.user_id=? GROUP BY Topic.id ORDER BY Topic.date_creation""", [id])
        result = cur.fetchall()
        return [{'id':topic[0], 'titre':topic[1], 'sscat_id':topic[2], 'nb_com':topic[3]} for topic in result]
  
    @classmethod
    def get_coms(cls, id):
        db = get_db()
        cur = db.execute("""SELECT Commentaire.id, Commentaire.topic_id, Commentaire.titre, Commentaire.text, Commentaire.date_creation, Commentaire.date_modification FROM Commentaire WHERE Commentaire.user_id=? ORDER BY Commentaire.date_creation""", [id])
        result = cur.fetchall()
        return [{'id':com[0],'topic_id':com[1],'titre':com[2],'text':com[3], 'date_creation':com[4], 'date_modification':com[5]} for com in result]



class Cat(object):
    """
    Class permettant de manipuler la table Categorie
    """
    @classmethod
    def insert(cls, titre):
        db = get_db()
        try:
            db.execute("""INSERT INTO Categorie (titre) VALUES (?)""", [titre])
            db.commit()
        except sqlite3.IntegrityError as e:
            print "Insert error for {cat} : {message}".format(cat=titre, message=e.message)

    @classmethod
    def get_cat(cls, titre):
        db = get_db()
        cur = db.execute("""SELECT id, titre, date_publication FROM Categorie WHERE titre=?""", [titre])
        result = cur.fetchone()
        if result:
            result = {
                'id': result[0],
                'titre': result[1],
                'date_publication': result[2]
            }
        return result

    @classmethod
    def get_cat_id(cls, id):
        db = get_db()
        cur = db.execute("""SELECT id, titre, date_publication FROM Categorie WHERE id=?""", [id])
        result = cur.fetchone()
        if result:
            result = {
                'id': result[0],
                'titre': result[1],
                'date_publication': result[2]
            }
        return result

    @classmethod
    def get_all_cat(cls):
        db = get_db()
        cur = db.execute("""SELECT id, titre, date_publication FROM Categorie ORDER BY date_creation""")
        result = cur.fetchall()
        return [{'id':cat[0], 'titre':cat[1], 'date_publication': cat[2]} for cat in result]


    @classmethod
    def get_sscats(cls, id):
        db = get_db()
        cur = db.execute("""SELECT id, titre, date_publication FROM Sous_cat WHERE categorie_id=? ORDER BY date_creation""", [id])
        result = cur.fetchall()
        return [{'id':sscat[0], 'titre':sscat[1], 'date_publication':sscat[2]} for sscat in result]



class Sous_cat(object):
    """
    Class permettant de manipuler la table Sous_cat
    """
    @classmethod
    def insert(cls, titre, cat_id):
        db = get_db()
        try:
            db.execute("""INSERT INTO Sous_cat (titre, categorie_id) VALUES (?, ?)""", [titre, cat_id])
            db.commit()
        except sqlite3.IntegrityError as e:
            print "Insert error for {sscat} : {message}".format(sscat=titre, message=e.message)

    @classmethod
    def get_sscat(cls, titre, cat_titre):
        db = get_db()
        cat=Cat.get_cat(cat_titre)
        if cat:
            cur = db.execute("""SELECT id, titre, date_publication, categorie_id FROM Sous_cat WHERE titre=? AND categorie_id=?""", [titre,  cat['id']])
            result = cur.fetchone()
            if result:
                result = {
                    'id': result[0],
                    'titre': result[1],
                    'date_publication': result[2],
                    'categorie_id': result[3]
                }
            return result

    @classmethod
    def get_sscat_id(cls, id):
        db = get_db()
        cur = db.execute("""SELECT id, titre, date_publication, categorie_id FROM Sous_cat WHERE id=?""", [id])
        result = cur.fetchone()
        if result:
            result = {
                'id': result[0],
                'titre': result[1],
                'date_publication': result[2],
                'cat_id': result[3]
            }
        return result

    @classmethod
    def get_topics(cls, id):
        db = get_db()
        cur = db.execute("""SELECT Topic.user_id, Topic.id, Topic.titre, COUNT(Commentaire.id) AS nb_com FROM Topic LEFT JOIN Commentaire ON Topic.id = Commentaire.topic_id WHERE Topic.sous_cat_id=? GROUP BY Topic.id ORDER BY Topic.date_publication""", [id])
        result = cur.fetchall()
        return [{'username':User.get_user_id(topic[0])['username'], 'user_id':topic[0], 'id':topic[1], 'titre':topic[2], 'nb_com':topic[3]} for topic in result]

    @classmethod
    def get_der_msg(cls, id):
        db=get_db()
        cur = db.execute("""SELECT MAX(Topic.date_publication), Topic.titre, Topic.id, User.username, User.id FROM Topic INNER JOIN User ON User.id = Topic.user_id WHERE Topic.sous_cat_id = ?""", [id])
        result = cur.fetchone()
        if(result[1]):
            result = {
                'date': result[0],
                'titre': result[1],
                'topic_id': result[2],
                'username': result[3],
                'user_id': result[4]
            }
            cur = db.execute("""SELECT MAX(Commentaire.date_creation), User.username, User.id FROM Commentaire INNER JOIN User ON User.id = Commentaire.user_id WHERE Commentaire.topic_id = ?""", [result['topic_id']])
            temp=cur.fetchone()
            if(temp[1]):
                result['username'] = temp[1]
                result['user_id'] = temp[2]
            return result
        return None



class Topic(object):
    """
    Class permettant de manipuler la table Topic
    """
    @classmethod
    def insert(cls, sscat_id, user_id, titre, text):
        db = get_db()
        try:
            db.execute("""INSERT INTO Topic (user_id, titre, text, sous_cat_id) VALUES (?, ?, ?, ?)""", [user_id, titre, text, sscat_id])
            db.commit()
        except sqlite3.IntegrityError as e:
            print "Insert error for {topic} : {message}".format(topic=titre, message=e.message)
        
    @classmethod
    def get_topic(cls, topic_id):
        db = get_db()
        cur = db.execute("""SELECT Topic.user_id, Topic.id, Topic.titre, Topic.text, COUNT(Commentaire.id) AS nb_com, Topic.sous_cat_id, Topic.date_creation, Topic.date_modification FROM Topic LEFT JOIN Commentaire ON Topic.id = Commentaire.topic_id WHERE Topic.id=?""", [topic_id])
        result = cur.fetchone()
        if result[1]:
            result = {
                'username': User.get_user_id(result[0])['username'],
                'user_id': result[0],
                'id': result[1],
                'titre': result[2],
                'text': result[3],
                'nb_com':result[4],
                'sscat_id':result[5],
                'date_creation':result[6],
                'date_modification':result[7]
            }
        else:
            return None
        return result

    @classmethod
    def get_coms(cls, id):
        db = get_db()
        cur = db.execute("""SELECT Commentaire.id, Commentaire.user_id, Commentaire.titre, Commentaire.text, Commentaire.date_creation, Commentaire.date_modification FROM Commentaire WHERE Commentaire.topic_id=? ORDER BY Commentaire.date_creation""", [id])
        result = cur.fetchall()
        return [{'id':com[0],'username':User.get_user_id(com[1])['username'], 'user_id':com[1],'titre':com[2],'text':com[3], 'date_creation':com[4], 'date_modification':com[5]} for com in result]



class Com(object):
    """
    Class permettant de manipuler la table Commentaire
    """
    @classmethod
    def insert(cls, topic_id, user_id, titre, text):
        db = get_db()
        try:
            db.execute("""INSERT INTO Commentaire (topic_id, user_id, titre, text) VALUES (?, ? ,?, ?)""", [topic_id, user_id, titre, text])
            # db.execute("""UPDATE Topic SET date_publication = (datetime('now', 'localtime')) WHERE Topic.id = ?""", [topic_id])
            # topic=Topic.get_topic(topic_id)
            # sscat=Sous_cat.get_sscat(topic['sscat'],topic['cat'])
            # db.execute("""UPDATE Sous_cat SET date_publication = (datetime('now', 'localtime')) WHERE Sous_cat.id = ?""", [sscat['id']])
            # cat=Cat.get_cat(topic['cat'])
            # db.execute("""UPDATE Categorie SET date_publication = (datetime('now', 'localtime')) WHERE Categorie.id = ?""", [cat['id']])
            db.commit()
        except sqlite3.IntegrityError as e:
            print "Insert error for {com} : {message}".format(com=titre, message=e.message)

    @classmethod
    def get_com(cls, com_id):
        db = get_db()
        cur = db.execute("""SELECT Commentaire.id, Commentaire.titre, Commentaire.text, Commentaire.topic_id, Commentaire.user_id, Commentaire.date_creation, Commentaire.date_modification FROM Commentaire WHERE Commentaire.id=?""", [com_id])
        result = cur.fetchone()
        if result:
            result = {
                'id': result[0],
                'titre': result[1],
                'text': result[2],
                'topic_id':result[3],
                'user_id': result[4],
                'date_creation':result[5],
                'date_modification':result[6]
            }
        return result