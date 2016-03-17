# coding=utf-8
from flask import Flask, url_for, render_template, request, redirect
import models
app = Flask(__name__)

@app.route('/')
@app.route('/<id>')
def acceuil(id=None):
    if request.method == 'GET':
        pass
    elif resquest.method == 'POST':
        pass
    cats=models.Cat.get_all_cat()
    for cat in cats:
    	cat['sscats'] = models.Sous_cat.get_all_sscat(cat['titre'])
    return render_template('index.html', cats = cats)


@app.route('/category/<id>')
def affichecat(id):
    if request.method == 'GET':
        pass
    elif resquest.method == 'POST':
        pass
    cat = models.Cat.get_cat_id(id)
    cat['sscats'] = models.Sous_cat.get_all_sscat(cat['titre'])
    return render_template('cat.html',cat=cat)

@app.route('/subcategory/<id>')
def affichesscat(id):
    if request.method == 'GET':
        pass
    elif resquest.method == 'POST':
        pass
    sscat = models.Sous_cat.get_sscat(id)
    sscat['topics'] = models.Topic.get_topic_cat(id)
    return render_template('sscat.html',sscat=sscat)


@app.route('/add_category')
def addcat():
    return render_template('add_cat.html')

@app.route('/add_subcategory')
def addsubcat():
    return render_template('add_subcat.html')

@app.route('/add_topic')
def addtopic():
    return render_template('add_topic.html')