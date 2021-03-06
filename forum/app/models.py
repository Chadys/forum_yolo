# coding=utf-8
from __future__ import absolute_import
import sqlite3
from flask import g


def connect_db():
    return sqlite3.connect('forum.db')


def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
        g.sqlite_db.execute("""PRAGMA foreign_keys = ON""")
    return g.sqlite_db


def nullify(champ):
    if (not champ):
        return None
    return champ


class User(object):
    """
    Class permettant de manipuler la table User
    """
    @classmethod
    def insert(cls, username, password, email, first_name, last_name, bday, sexe):
        db = get_db()
        try:
            first_name, last_name, bday, sexe = nullify(first_name), nullify(last_name), nullify(bday), nullify(sexe)
            db.execute("""INSERT INTO User (username, password, email, prenom, nom, date_naiss, sexe) VALUES (?, ?, ?, ?, ?, ?, ?)""", [username, password, email, first_name, last_name, bday, sexe])
            db.commit()
        except sqlite3.IntegrityError as e:
            print "Insert error for {user} : {message}".format(user=username, message=e.message)

    @classmethod
    def get_user(cls, id):
        db = get_db()
        cur = db.execute("""SELECT id, username, email, date_creation, date_connection, nom, prenom, date_naiss, sexe, password, permission FROM User WHERE id=?""", [id])
        result = cur.fetchone()
        if result:
            result = {
                'id': result[0],
                'username': result[1] if result[10] else result[1]+' (BANNED)',
                'email': result[2],
                'date_creation': result[3],
                'date_connection': result[4],
                'nom': result[5],
                'prenom': result[6],
                'date_naiss': result[7],
                'sexe': result[8],
                'password': result[9],
                'permission':result[10]
            }
        return result

    @classmethod
    def get_user_id(cls, username):
        db = get_db()
        cur = db.execute("""SELECT id  FROM User WHERE username=?""", [username])
        result = cur.fetchone()
        if result:
            result = result[0]
        return result

    @classmethod
    def get_user_id_by_mail(cls, email):
        db = get_db()
        cur = db.execute("""SELECT id  FROM User WHERE email=?""", [email])
        result = cur.fetchone()
        if result:
            result = result[0]
        return result

    @classmethod
    def get_all_users(cls):
        db = get_db()
        cur = db.execute("""SELECT id, username, date_creation, date_connection, permission FROM User ORDER BY id""")
        result = cur.fetchall()
        return [{'id':user[0], 'username':user[1] if user[4] else user[1]+' (BANNED)', 'date_creation':user[2], 'date_connection':user[3], 'permission':user[4]} for user in result]

    @classmethod
    def update_connect(cls, id):
        db = get_db()
        db.execute("""UPDATE User SET date_connection = (datetime('now', 'localtime')) WHERE id=?""", [id])
        db.commit()

    @classmethod
    def get_topics(cls, id):
        db = get_db()
        cur = db.execute("""SELECT Topic.id, Topic.titre, Topic.sous_cat_id, Topic.hidden, COUNT(Commentaire.id) AS nb_com FROM Topic LEFT JOIN Commentaire ON Topic.id = Commentaire.topic_id WHERE Topic.user_id=? GROUP BY Topic.id ORDER BY Topic.date_creation""", [id])
        result = cur.fetchall()
        return [{'id':topic[0], 'titre':topic[1], 'sscat_id':topic[2], 'sscat_titre':Sous_cat.get_sscat(topic[2])['titre'], 'hidden':topic[3], 'nb_com':topic[4]} for topic in result]
  
    @classmethod
    def get_coms(cls, id):
        db = get_db()
        cur = db.execute("""SELECT Commentaire.id, Commentaire.topic_id, Commentaire.titre, Commentaire.text, Commentaire.date_creation, Commentaire.date_modification FROM Commentaire WHERE Commentaire.user_id=? ORDER BY Commentaire.date_creation""", [id])
        result = cur.fetchall()
        i=0
        for com in result:
            com = {'id':com[0],'topic_id':com[1],'titre':com[2],'text':com[3], 'date_creation':com[4], 'date_modification':com[5]}
            topic=Topic.get_topic(com['topic_id'])
            sscat=Sous_cat.get_sscat(topic['sscat_id'])
            com['topic_titre']=topic['titre']
            com['sscat_id']=sscat['id']
            com['sscat_titre']=sscat['titre']
            result[i]=com
            i+=1
        return result

    @classmethod
    def update(cls, id, username, password, email, first_name, last_name, bday, sexe):
        db = get_db()
        try:
            first_name, last_name, bday, sexe = nullify(first_name), nullify(last_name), nullify(bday), nullify(sexe)
            db.execute("""UPDATE User SET username=?, password=?, email=?, prenom=?, nom=?, date_naiss=?, sexe=? WHERE id=?""", [username, password, email, first_name, last_name, bday, sexe, id])
            db.commit()
        except sqlite3.IntegrityError as e:
            if not password:
                db.execute("""UPDATE User SET username=?, email=?, prenom=?, nom=?, date_naiss=?, sexe=? WHERE id=?""", [username, email, first_name, last_name, bday, sexe, id])
                db.commit()
            else:
                print "Update error for {user} : {message}".format(user=username, message=e.message)
            
    @classmethod
    def update_permission(cls, id, perm):
        db = get_db()
        try:
            db.execute("""UPDATE User SET permission=? WHERE id=?""", [perm, id])
            db.commit()
        except sqlite3.IntegrityError as e:
            print "Update error for {user} : {message}".format(user=username, message=e.message)

    @classmethod
    def delete(cls, id):
        db = get_db()
        try:
            db.execute("""DELETE FROM User WHERE id=?""", [id])
            db.commit()
        except sqlite3.IntegrityError as e:
            print "Delete error for user {id} : {message}".format(id=id, message=e.message)




class Cat(object):
    """
    Class permettant de manipuler la table Categorie
    """
    @classmethod
    def insert(cls, titre, hidden):
        db = get_db()
        try:
            db.execute("""INSERT INTO Categorie (titre, hidden) VALUES (?,?)""", [titre,hidden])
            db.commit()
        except sqlite3.IntegrityError as e:
            print "Insert error for {cat} : {message}".format(cat=titre, message=e.message)

    @classmethod
    def get_cat_id(cls, titre):
        db = get_db()
        cur = db.execute("""SELECT id FROM Categorie WHERE titre=?""", [titre])
        result = cur.fetchone()
        if result:
            result = result[0]
        return result

    @classmethod
    def get_cat(cls, id):
        db = get_db()
        cur = db.execute("""SELECT id, titre, date_publication, hidden FROM Categorie WHERE id=?""", [id])
        result = cur.fetchone()
        if result:
            result = {
                'id': result[0],
                'titre': result[1],
                'date_publication': result[2],
                'hidden': result[3]
            }
        return result

    @classmethod
    def get_all_cat(cls):
        db = get_db()
        cur = db.execute("""SELECT id, titre, date_publication, hidden FROM Categorie ORDER BY date_creation""")
        result = cur.fetchall()
        return [{'id':cat[0], 'titre':cat[1], 'date_publication': cat[2], 'hidden': cat[3]} for cat in result]


    @classmethod
    def get_sscats(cls, id):
        db = get_db()
        cur = db.execute("""SELECT id, titre, description, date_publication, hidden FROM Sous_cat WHERE categorie_id=? ORDER BY date_creation""", [id])
        result = cur.fetchall()
        return [{'id':sscat[0], 'titre':sscat[1], 'description':sscat[2], 'date_publication':sscat[3], 'hidden': sscat[4]} for sscat in result]

    @classmethod
    def edit(cls, id, titre, hidden):
        db = get_db()
        try:
            cur = db.execute("""UPDATE Categorie SET titre=?, hidden=? WHERE Categorie.id=?""", [titre,hidden,id])
            db.commit()
        except sqlite3.IntegrityError as e:
            print "Update error for {cat} : {message}".format(cat=titre, message=e.message)

    @classmethod
    def delete(cls, id):
        db = get_db()
        try:
            db.execute("""DELETE FROM Categorie WHERE Categorie.id=?""", [id])
            db.commit()
        except sqlite3.IntegrityError as e:
            print "Delete error for category {id} : {message}".format(id=id, message=e.message)



class Sous_cat(object):
    """
    Class permettant de manipuler la table Sous_cat
    """
    @classmethod
    def insert(cls, titre, descr, cat_id, hidden):
        db = get_db()
        try:
            db.execute("""INSERT INTO Sous_cat (titre, description, categorie_id, hidden) VALUES (?, ?, ?, ?)""", [titre, descr, cat_id, hidden])
            db.commit()
        except sqlite3.IntegrityError as e:
            print "Insert error for {sscat} : {message}".format(sscat=titre, message=e.message)

    @classmethod
    def get_sscat_id(cls, titre, cat_titre):
        db = get_db()
        cat_id=Cat.get_cat_id(cat_titre)
        if cat_id:
            cur = db.execute("""SELECT id FROM Sous_cat WHERE titre=? AND categorie_id=?""", [titre,  cat_id])
            result = cur.fetchone()
            if result:
                result = result[0]
            return result
        return None

    @classmethod
    def get_sscat(cls, id):
        db = get_db()
        cur = db.execute("""SELECT id, titre, description, date_publication, categorie_id, hidden FROM Sous_cat WHERE id=?""", [id])
        result = cur.fetchone()
        if result:
            result = {
                'id': result[0],
                'titre': result[1],
                'description': result[2],
                'date_publication': result[3],
                'cat_id': result[4],
                'hidden': result[5]
            }
        return result

    @classmethod
    def get_topics(cls, id):
        db = get_db()
        cur = db.execute("""SELECT Topic.user_id, Topic.id, Topic.titre, Topic.hidden, COUNT(Commentaire.id) AS nb_com FROM Topic LEFT JOIN Commentaire ON Topic.id = Commentaire.topic_id WHERE Topic.sous_cat_id=? GROUP BY Topic.id ORDER BY Topic.date_publication DESC""", [id])
        result = cur.fetchall()
        return [{'user_id':topic[0], 'id':topic[1], 'titre':topic[2], 'hidden':topic[3], 'nb_com':topic[4], 'username':User.get_user(topic[0])['username'] if topic[0] else 'Deleted user'} for topic in result]
                
    @classmethod
    def get_der_msg(cls, id):
        db=get_db()
        cur = db.execute("""SELECT MAX(Topic.date_publication), Topic.titre, Topic.id, Topic.hidden, User.username, User.id FROM Topic LEFT JOIN User ON User.id = Topic.user_id WHERE Topic.sous_cat_id = ?""", [id])
        result = cur.fetchone()
        if(result[1]):
            result = {
                'date': result[0],
                'titre': result[1],
                'topic_id': result[2],
                'hidden': result[3],
                'username': result[4],
                'user_id': result[5]
            }
            if not result['username']:
                result['username'] = 'Deleted user'
            cur = db.execute("""SELECT MAX(Commentaire.date_creation), Commentaire.id, User.username, User.id FROM Commentaire LEFT JOIN User ON User.id = Commentaire.user_id WHERE Commentaire.topic_id = ?""", [result['topic_id']])
            temp=cur.fetchone()
            if(temp[1]):
                result['username'] = temp[2] if temp[2] else 'Deleted user'
                result['user_id'] = temp[3]
            return result
        return None

    @classmethod
    def edit(cls, id, titre, descr, hidden):
        db = get_db()
        try:
            cur = db.execute("""UPDATE Sous_cat SET titre=?, description=?, hidden=? WHERE Sous_cat.id=?""", [titre,descr,hidden,id])
            db.commit()
        except sqlite3.IntegrityError as e:
            print "Update error for {sscat} : {message}".format(sscat=titre, message=e.message)

    @classmethod
    def delete(cls, id):
        db = get_db()
        try:
            db.execute("""DELETE FROM Sous_cat WHERE Sous_cat.id=?""", [id])
            db.commit()
        except sqlite3.IntegrityError as e:
            print "Delete error for subcategory {id} : {message}".format(id=id, message=e.message)



class Topic(object):
    """
    Class permettant de manipuler la table Topic
    """
    @classmethod
    def insert(cls, sscat_id, user_id, titre, text, hidden):
        db = get_db()
        try:
            db.execute("""INSERT INTO Topic (user_id, titre, text, sous_cat_id, hidden) VALUES (?, ?, ?, ?, ?)""", [user_id, titre, text, sscat_id, hidden])
            db.commit()
        except sqlite3.IntegrityError as e:
            print "Insert error for {topic} : {message}".format(topic=titre, message=e.message)
        
    @classmethod
    def get_topic(cls, topic_id):
        db = get_db()
        cur = db.execute("""SELECT Topic.user_id, Topic.id, Topic.titre, Topic.text, Topic.hidden, COUNT(Commentaire.id) AS nb_com, Topic.sous_cat_id, Topic.date_creation, Topic.date_modification FROM Topic LEFT JOIN Commentaire ON Topic.id = Commentaire.topic_id WHERE Topic.id=?""", [topic_id])
        result = cur.fetchone()
        if result[1]:
            result = {
                'user_id': result[0],
                'id': result[1],
                'titre': result[2],
                'text': result[3],
                'hidden':result[4],
                'nb_com':result[5],
                'sscat_id':result[6],
                'date_creation':result[7],
                'date_modification':result[8],
                'username':User.get_user(result[0])['username'] if result[0] else 'Deleted user'
            }
            return result
        return None

    @classmethod
    def get_coms(cls, id):
        db = get_db()
        cur = db.execute("""SELECT Commentaire.id, Commentaire.user_id, Commentaire.titre, Commentaire.text, Commentaire.date_creation, Commentaire.date_modification FROM Commentaire WHERE Commentaire.topic_id=? ORDER BY Commentaire.date_creation""", [id])
        result = cur.fetchall()
        return [{'id':com[0], 'user_id':com[1],'titre':com[2],'text':com[3], 'date_creation':com[4], 'date_modification':com[5], 'username':User.get_user(com[1])['username'] if com[1] else 'Deleted user'} for com in result]

    @classmethod
    def edit(cls, id, text, titre, hidden):
        db = get_db()
        try:
            cur = db.execute("""UPDATE Topic SET titre=?, text=?, hidden=? WHERE Topic.id=?""", [titre,text,hidden,id])
            db.commit()
        except sqlite3.IntegrityError as e:
            print "Update error for this topic : {message}".format(message=e.message)

    @classmethod
    def delete(cls, id):
        db = get_db()
        try:
            db.execute("""DELETE FROM Topic WHERE Topic.id=?""", [id])
            db.commit()
        except sqlite3.IntegrityError as e:
            print "Delete error for topic {id} : {message}".format(id=id, message=e.message)

    @classmethod
    def moderate(cls, id, modo):
        db = get_db()
        try:
            text = 'Moderated by '+modo
            cur = db.execute("""UPDATE Topic SET text=? WHERE Topic.id=?""", [text,id])
            db.commit()
        except sqlite3.IntegrityError as e:
            print "Update error for this topic : {message}".format(message=e.message)



class Com(object):
    """
    Class permettant de manipuler la table Commentaire
    """
    @classmethod
    def insert(cls, topic_id, user_id, titre, text):
        db = get_db()
        try:
            db.execute("""INSERT INTO Commentaire (topic_id, user_id, titre, text) VALUES (?, ? ,?, ?)""", [topic_id, user_id, titre, text])
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

    @classmethod
    def edit(cls, id, titre, text):
        db = get_db()
        try:
            cur = db.execute("""UPDATE Commentaire SET titre=?, text=? WHERE Commentaire.id=?""", [titre,text,id])
            db.commit()
        except sqlite3.IntegrityError as e:
            print "Update error for this comment : {message}".format(message=e.message)

    @classmethod
    def delete(cls, id):
        db = get_db()
        try:
            db.execute("""DELETE FROM Commentaire WHERE Commentaire.id=?""", [id])
            db.commit()
        except sqlite3.IntegrityError as e:
            print "Delete error for comment {id} : {message}".format(id=id, message=e.message)

    @classmethod
    def moderate(cls, id, modo):
        db = get_db()
        try:
            text = 'Moderated by '+modo
            cur = db.execute("""UPDATE Commentaire SET text=? WHERE Commentaire.id=?""", [text,id])
            db.commit()
        except sqlite3.IntegrityError as e:
            print "Update error for this comment : {message}".format(message=e.message)