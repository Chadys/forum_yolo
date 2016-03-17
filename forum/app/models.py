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
    def inserts(cls, users):
        """
        :param users:
        :type users: tableau d'user [[username, password, email]]
        :return:
        :rtype:
        """
        db = get_db()
        db.execute("""INSERT INTO User (username, password, email) VALUES (?, ? ,?)""", users)
        db.commit()

    @classmethod
    def get_user(cls, username):
        db = get_db()
        cur = db.execute("""SELECT id, username, email FROM User WHERE username=?""", [username])
        result = cur.fetchone()
        if result:
            result = {
                'id': result[0],
                'username': result[1],
                'email': result[2]
            }
        return result



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
        cur = db.execute("""SELECT id, titre FROM Categorie WHERE titre=?""", [titre])
        result = cur.fetchone()
        if result:
            result = {
                'id': result[0],
                'titre': result[1]
            }
        return result

    @classmethod
    def get_cat_id(cls, id):
        db = get_db()
        cur = db.execute("""SELECT id, titre FROM Categorie WHERE id=?""", [id])
        result = cur.fetchone()
        if result:
            result = {
                'id': result[0],
                'titre': result[1]
            }
        return result

    @classmethod
    def get_all_cat(cls):
        db = get_db()
        cur = db.execute("""SELECT id, titre FROM Categorie""")
        result = cur.fetchall()
        return [{'id':cat[0], 'titre':cat[1]} for cat in result]




class Sous_cat(object):
    """
    Class permettant de manipuler la table Sous_cat
    """
    @classmethod
    def insert(cls, titre, cat_titre):
        db = get_db()
        cat=Cat.get_cat(cat_titre)
        try:
            db.execute("""INSERT INTO Sous_cat (titre, categorie_id) VALUES (?, ?)""", [titre, cat['id']])
            db.commit()
        except sqlite3.IntegrityError as e:
            print "Insert error for {sscat} : {message}".format(sscat=titre, message=e.message)

    @classmethod
    def get_sscat(cls, titre, cat_titre):
        db = get_db()
        cat=Cat.get_cat(cat_titre)
        if cat:
            cur = db.execute("""SELECT id, titre FROM Sous_cat WHERE titre=? AND categorie_id=?""", [titre,  cat['id']])
            result = cur.fetchone()
            if result:
                result = {
                    'id': result[0],
                    'titre': result[1]
                }
            return result

    @classmethod
    def get_sscat(cls, id):
        db = get_db()
        cur = db.execute("""SELECT id, titre FROM Sous_cat WHERE id=?""", [id])
        result = cur.fetchone()
        if result:
            result = {
                'id': result[0],
                'titre': result[1]
            }
        return result

    @classmethod
    def get_all_sscat(cls, cat_titre):
        db = get_db()
        cat=Cat.get_cat(cat_titre)
        if cat:
            cur = db.execute("""SELECT id, titre FROM Sous_cat WHERE categorie_id=?""", [cat['id']])
            result = cur.fetchall()
            return [{'id':sscat[0], 'titre':sscat[1]} for sscat in result]




class Topic(object):
    """
    Class permettant de manipuler la table Topic
    """
    @classmethod
    def insert(cls, username, titre, text, cat, souscat):
        db = get_db()
        user=User.get_user(username)
        sscat = Sous_cat.get_sscat(souscat,cat)
        try:
            db.execute("""INSERT INTO Topic (user_id, titre, text, sous_cat_id) VALUES (?, ?, ?, ?)""", [user['id'], titre, text, sscat['id']])
            db.commit()
        except sqlite3.IntegrityError as e:
            print "Insert error for {topic} : {message}".format(topic=titre, message=e.message)
        except TypeError as e:
            print "Insert error for {topic} : {message}".format(topic=titre, message=e.message)
    
    @classmethod
    def get_topic_user(cls, username):
        db = get_db()
        user=User.get_user(username)
        cur = db.execute("""SELECT Topic.id, Topic.titre, Sous_cat.titre, Categorie.titre, COUNT(Commentaire.id) AS nb_com FROM Topic INNER JOIN Sous_cat ON Sous_cat.id=Topic.sous_cat_id INNER JOIN Categorie ON Sous_cat.categorie_id=Categorie.id INNER JOIN Commentaire ON Topic.id = Commentaire.topic_id WHERE Topic.user_id=? ORDER BY Topic.date_modification""", [user['id']])
        result = cur.fetchall()
        return [{'id':topic[0], 'titre':topic[1], 'sscat':topic[2], 'cat':topic[3], 'nb_com':topic[4]} for topic in result]
    
    @classmethod
    def get_topic_cat(cls, ss_cat_id):
        db = get_db()
        cur = db.execute("""SELECT User.username, Topic.id, Topic.titre, COUNT(Commentaire.id) AS nb_com FROM Topic INNER JOIN User ON User.id=Topic.user_id INNER JOIN Sous_cat ON Sous_cat.id=Topic.sous_cat_id INNER JOIN Commentaire ON Topic.id = Commentaire.topic_id WHERE Sous_cat.id=? ORDER BY Topic.date_publication""", [ss_cat_id])
        result = cur.fetchall()
        return [{'user':topic[0], 'id':topic[1], 'titre':topic[2], 'nb_com':topic[3]} for topic in result]

    @classmethod
    def get_topic(cls, topic_id):
        db = get_db()
        cur = db.execute("""SELECT User.username, Topic.id, Topic.titre, Sous_cat.titre, Categorie.titre, COUNT(Commentaire.id) AS nb_com FROM Topic INNER JOIN User ON User.id=Topic.user_id INNER JOIN Sous_cat ON Sous_cat.id=Topic.sous_cat_id INNER JOIN Categorie ON Sous_cat.categorie_id=Categorie.id INNER JOIN Commentaire ON Topic.id = Commentaire.topic_id WHERE Topic.id=?""", [topic_id])
        result = cur.fetchone()
        if result:
            result = {
                'user': result[0],
                'id': result[1],
                'titre': result[2],
                'sscat': result[3],
                'cat': result[4],
                'nb_com':topic[5]
            }
        return result

class Com(object):
    """
    Class permettant de manipuler la table Commentaire
    """
    @classmethod
    def insert(cls, topic_id, username, titre, text):
        db = get_db()
        user=User.get_user(username)
        try:
            db.execute("""INSERT INTO Commentaire (topic_id, user_id, titre, text) VALUES (?, ? ,?, ?)""", [topic_id, user['id'], titre, text])
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
    def get_com_topic(cls, topic_id):
        db = get_db()
        cur = db.execute("""SELECT Commentaire.id, User.username, Commentaire.titre, Commentaire.text FROM Commentaire INNER JOIN Topic ON Topic.id=Commentaire.topic_id INNER JOIN User ON User.id=Commentaire.user_id WHERE Commentaire.topic_id=? ORDER BY Commentaire.date_creation""", [topic_id])
        result = cur.fetchall()
        return [{'id':com[0],'username':com[1],'titre':com[2],'text':com[3]} for com in result]

    @classmethod
    def get_com_user(cls, username):
        db = get_db()
        user=User.get_user(username)
        cur = db.execute("""SELECT Commentaire.id, Topic.titre, Commentaire.titre, Commentaire.text FROM Commentaire INNER JOIN Topic ON Topic.id=Commentaire.topic_id INNER JOIN User ON User.id=Commentaire.user_id WHERE Commentaire.user_id=? ORDER BY Commentaire.date_creation""", [user['id']])
        result = cur.fetchall()
        return [{'id':com[0],'post':com[1],'titre':com[2],'text':com[3]} for com in result]
       