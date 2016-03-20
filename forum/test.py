# coding=utf-8
import sqlite3

from app.models import User, Cat, Sous_cat, Topic, Com
from app.views import app
with app.app_context():
    User.insert('toto', 'toot', 'toto.toto@iedparis8.net')
    User.insert('julie', 'yolo', 'julie.rymer@iedparis8.net')
    User.insert('truc', 'machin', 'truc.machin@iedparis8.net')
    print User.get_user('truc')
    print User.get_user('s')
    Cat.insert('Theme')
    Cat.insert('Jeux')
    Cat.insert('Technologie')
    print Cat.get_cat('Yolo')
    print Cat.get_cat('Jeux')
    print Cat.get_all_cat()
    Sous_cat.insert('Couleurs','Theme')
    Sous_cat.insert('Fleurs','Theme')
    Sous_cat.insert('Videos','Jeux')
    Sous_cat.insert('Cartes','Jeux')
    Sous_cat.insert('Videos','Technologie')
    Sous_cat.insert('Photos','Technologie')
    Sous_cat.insert('Robots','Technologie')
    print Sous_cat.get_sscat('Fleurs','Theme')
    print Sous_cat.get_all_sscat('Theme')
    Topic.insert('troc','t','t','t','t')
    Topic.insert('truc','Sonic','Le herisson, c''est trop bon!','Jeux','Videos')
    Topic.insert('toto','Mario','Le plombier c''est la nouvelle mode de l''ete','Jeux','Videos')
    print Topic.get_topic_user('toto')
    print Topic.get_topic_cat(4)
    print Topic.get_topic(1)
    Com.insert(Topic.get_topic_user('toto')[0]['id'],'truc',None,'Les plombiers ils montrent leur raie du cul, c''est degueulasse')
    Com.insert(Topic.get_topic_user('truc')[0]['id'],'toto',None,'Bwaaah ca va pas ! On mange pas les oursins terrestre !')
    print Com.get_com_topic(Topic.get_topic_user('truc')[0]['id'])
    print Com.get_com_user('truc')

    #from flask import g
    
    #if not hasattr(g, 'sqlite_db'):
    #    g.sqlite_db = sqlite3.connect('forum.db')
    #db = g.sqlite_db

    #cur = db.execute("""SELECT date_publication FROM Sous_cat""")
    #print cur.fetchall()

    #Topic.insert('toto','Mario','Le plombier c''est la nouvelle mode de l''ete','Jeux','Videos')

    #cur = db.execute("""SELECT date_publication FROM Sous_cat""")
    #print cur.fetchall()