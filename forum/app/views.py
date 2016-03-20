# coding=utf-8
from flask import Flask, url_for, render_template, request, redirect, abort
import models, ipdb
app = Flask(__name__)

@app.route('/')
@app.route('/<int:id>')
def acceuil(id=None):
    if request.method == 'GET':
        pass
    elif resquest.method == 'POST':
        pass
    cats=models.Cat.get_all_cat()
    for cat in cats:
    	cat['sscats'] = models.Cat.get_sscats(cat['id'])
        for sscat in cat['sscats']:
            sscat['der_msg'] = models.Sous_cat.get_der_msg(sscat['id'])
    return render_template('index.html', cats = cats)



@app.route('/category/<int:id>')
def affichecat(id):
    if request.method == 'GET':
        pass
    elif resquest.method == 'POST':
        pass
    cat = models.Cat.get_cat_id(id)
    cat['sscats'] = models.Cat.get_sscats(cat['id'])
    return render_template('cat.html',cat=cat)

@app.route('/subcategory/<int:id>')
def affichesscat(id):
    if request.method == 'GET':
        pass
    elif resquest.method == 'POST':
        pass
    sscat = models.Sous_cat.get_sscat_id(id)
    sscat['topics'] = models.Sous_cat.get_topics(id)
    cat = models.Cat.get_cat_id(sscat['cat_id'])
    return render_template('sscat.html',sscat=sscat,cat=cat)

@app.route('/topic/<int:id>')
def affichetopic(id):
    if request.method == 'GET':
        pass
    elif resquest.method == 'POST':
        pass
    topic = models.Topic.get_topic(id)
    topic['com'] = models.Topic.get_coms(id)
    sscat=models.Sous_cat.get_sscat_id(topic['sscat_id'])
    cat=models.Cat.get_cat_id(sscat['cat_id'])
    return render_template('topic.html',topic=topic,sscat=sscat,cat=cat)



@app.route('/add_category', methods=['GET', 'POST'])
def addcat():
    try:
        return edit_content('category')
    except TypeError as e:
        print "TypeError : {message}".format(message=e.message)
        abort(404)

@app.route('/add_subcategory/<int:cat_id>', methods=['GET', 'POST'])
def addsubcat(cat_id):
    try:
        return add_content('subcategory',cat_id)
    except TypeError as e:
        print "TypeError : {message}".format(message=e.message)
        abort(404)

@app.route('/add_topic/<int:sscat_id>', methods=['GET', 'POST'])
def addtopic(sscat_id):
    try:
        return add_content('topic',sscat_id,1)
    except TypeError as e:
        print "TypeError : {message}".format(message=e.message)
        abort(404)

@app.route('/add_com/<int:topic_id>', methods=['GET', 'POST'])
def addcom(topic_id):
    try:
        return add_content('comment',topic_id, 1)
    except TypeError as e:
        print "TypeError : {message}".format(message=e.message)
        abort(404)

def add_content(type, container_id=None, user_id=None):
    champs={}
    if(type == 'comment'):
        champs['requis'] = ['content']
        container = models.Topic.get_topic(container_id)['titre']
        back = url_for('affichetopic', id=container_id)
    elif(type == 'topic'):
        champs['requis'] = ['title','content']
        container = models.Sous_cat.get_sscat_id(container_id)['titre']
        back = url_for('affichesscat', id=container_id)
    elif(type == 'subcategory'):
        champs['requis'] = ['title']
        container = models.Cat.get_cat_id(container_id)['titre']
        back = url_for('affichecat', id=container_id)
    else:
        champs['requis'] = ['title']
        container = 'the forum'
        back = '/'

    if request.method == 'GET':
        return render_template('add_content.html', form={}, errors={}, type=type, container=container, back=back)
    else:
        # ipdb.set_trace()
        form = request.form
        result =  validate(form, champs)
        if result['valid']:
            if(type == 'comment'):
                models.Com.insert(container_id,user_id, result['form']['title'], result['form']['content'])
            elif(type == 'topic'):
                models.Topic.insert(container_id,user_id, result['form']['title'], result['form']['content'])
            elif(type == 'subcategory'):
                if(not unique_sscat(container,result['form']['title'],result['errors'])):
                    return render_template('add_content.html',form=result['form'], errors=result['errors'], type=type, container=container, back=back)
                models.Sous_cat.insert(result['form']['title'],container_id)
            else:
                if(not unique_cat(result['form']['title'],result['errors'])):
                    return render_template('add_content.html',form=result['form'], errors=result['errors'], type=type, container=container, back=back)
                models.Cat.insert(result['form']['title'])
            return redirect(back)
        else:
            return render_template('add_content.html',form=result['form'], errors=result['errors'], type=type, container=container, back=back)



@app.route('/edit_category/<int:cat_id>', methods=['GET', 'POST'])
def editcat(cat_id):
    cat = models.Cat.get_cat_id(cat_id)
    if(cat):
        return edit_content(cat,'category')
    print "Category {} not found".format(cat_id)
    abort(404)

@app.route('/edit_subcategory/<int:sscat_id>', methods=['GET', 'POST'])
def editsubcat(sscat_id):
    sscat = models.Sous_cat.get_sscat_id(sscat_id)
    if(sscat):
        return edit_content(sscat,'subcategory')
    print "Subcategory {} not found".format(sscat_id)
    abort(404)

@app.route('/edit_topic/<int:topic_id>', methods=['GET', 'POST'])
def edittopic(topic_id):
    topic = models.Topic.get_topic(topic_id)
    if(topic):
        return edit_content(topic,'topic')
    print "Topic {} not found".format(topic_id)
    abort(404)

@app.route('/edit_com/<int:com_id>', methods=['GET', 'POST'])
def editcom(com_id):
    com = models.Com.get_com(com_id)
    if(com):
        return edit_content(com,'comment')
    print "Comment {} not found".format(com_id)
    abort(404)

def edit_content(this,type):
    champs={}
    if(type in {'comment', 'topic'}):
        champs['requis'] = ['content']
        form = {'title':this['titre'],'content':this['text']}
        if(type == 'comment'):
            back = url_for('affichetopic', id=this['topic_id'])
        else:
            back = url_for('affichetopic', id=this['id'])
    else:
        champs['requis'] = ['title']
        form = {'title':this['titre']}
        if(type == 'subcategory'):
            back = url_for('affichesscat', id=this['id'])
        else:
            back = url_for('affichecat', id=this['id'])

    if request.method == 'GET':
        return render_template('manage_content.html', form=form, errors={}, type=type, this=this, back=back)
    else:
        form = request.form
        result =  validate(form, champs)
        if result['valid']:
            if(type == 'comment'):
                pass
            elif(type == 'topic'):
                pass
            elif(type == 'subcategory'):
                if(not unique_sscat(container,result['form']['title'],result['errors'])):
                    return render_template('manage_content.html',form=result['form'], errors=result['errors'], type=type, this=this, back=back)

            else:
                if(not unique_cat(result['form']['title'],result['errors'])):
                    return render_template('manage_content.html',form=result['form'], errors=result['errors'], type=type, this=this, back=back)


            return redirect(back)
        else:
            return render_template('manage_content.html',form=result['form'], errors=result['errors'], type=type, this=this, back=back)




def unique_sscat(cat_titre, sscat_titre, errors):
    if(models.Sous_cat.get_sscat(sscat_titre, cat_titre)):
        errors['title'] = 'This name is already used in {}'.format(cat_titre)
        return False
    return True

def unique_cat(cat_titre, errors):
    if(models.Cat.get_cat(cat_titre)):
        errors['title'] = 'A category with this name already exists'
        return False
    return True


def validate(form, champs):
    result = {'valid': True, 'form': form, 'errors': {}}
    for champ in champs['requis']:
        result['valid'] = champ_requis(form, champ, result['errors']) and result['valid']

    return result

def champ_requis(form, champ, errors):
    if form[champ] == '':
        errors[champ] = 'A {} is required'.format(champ)
        return False
    else:
        return True