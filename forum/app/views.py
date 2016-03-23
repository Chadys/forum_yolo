# coding=utf-8
from flask import Flask, url_for, render_template, request, redirect, abort, Markup, session
from bcrypt import hashpw, gensalt
from functools import wraps
from validate_email import validate_email
import models, ipdb, re, datetime
app = Flask(__name__)
app.secret_key = '\x80\x7f\x14\xfe\x0eT\xe6y\xf8\xbff\xe78\xaf\x88~1\xc8\x95\xca&\x1dc!\xe7'




# -------------------------------------------- SESSION AND ERRORS CONTROL ------------------------------------------------ #




@app.route('/login', methods=['GET', 'POST'])
def login():
    champs={'requis':['pseudo', 'password']}

    if request.method == 'GET':
        return render_template('login.html', form={}, errors={})
    else:
        form = request.form
        result =  validate(form, champs)
        if result['valid']:
            user = identify(result['form']['pseudo'], result['form']['password'], result['errors'])
            if user:
                session['id']=user['id']
                session['username']=user['username']
                #session['permission']=user['permission']
                if(result['form'].get('permanent',None)):
                    session.permanent=True
                else:
                    session.permanent=False
                models.User.update_connect(session['id'])
                return redirect('/')
        return render_template('login.html',form=result['form'], errors=result['errors'])

@app.route('/logout')
def logout():
    session.pop('id', None)
    session.pop('username', None)
    #session.pop('permission', None)
    return redirect('/')

@app.route('/register', methods=['GET', 'POST'])
def register():
    champs={'requis':['pseudo', 'password', 'passwordbis', 'email'], 'pseudo':['pseudo'], 'email':['email'], 'pwd':['password', 'passwordbis'], 'date':'bday', 'check':['chart'], 'name':['fname','lname']}

    if request.method == 'GET':
        return render_template('register.html', form={}, errors={})
    else:
        form = request.form
        result =  validate(form, champs)
        if result['valid']:
            #ipdb.set_trace()
            models.User.insert(result['form']['pseudo'],hashpw(result['form']['password'].encode('UTF_8'), gensalt()),result['form']['email'],result['form']['fname'],result['form']['lname'],result['form']['bday'],result['form']['sexe'])
            return redirect('/register/succcess')
        return render_template('register.html',form=result['form'], errors=result['errors'])

@app.route('/register/succcess')
def registration_complete():
    return render_template('registration_complete.html')

def deny_access(error):
    def decorator(func):
        @wraps(func)
        #ipdb.set_trace()
        def wrapper(*args,**kwargs):
            if(session.get('id',None)):
                return func(*args,**kwargs)
            return abort(error)
        return wrapper
    return decorator

@app.errorhandler(400)
def bad_request(error):
    return render_template('error.html',error=error, code=400), 400
@app.errorhandler(401)
def unauthorized(error):
    return render_template('error.html',error=error, code=401), 401
@app.errorhandler(403)
def forbidden(error):
    return render_template('error.html',error=error, code=403), 403
@app.errorhandler(404)
def not_found(error):
    return render_template('error.html',error=error, code=404), 404




# -------------------------------------------- DISPLAY CONTENT ------------------------------------------------ #




def myrender(func):
    def wrapper(template,**kwargs):
        return func(template, session=session, **kwargs)
    return wrapper

render_template=myrender(render_template)

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
    cat = models.Cat.get_cat(id)
    if(not cat):
        abort(404)
    cat['sscats'] = models.Cat.get_sscats(cat['id'])
    return render_template('cat.html',cat=cat)

@app.route('/subcategory/<int:id>')
def affichesscat(id):
    if request.method == 'GET':
        pass
    elif resquest.method == 'POST':
        pass
    sscat = models.Sous_cat.get_sscat(id)
    if(not sscat):
        abort(404)
    sscat['topics'] = models.Sous_cat.get_topics(id)
    cat = models.Cat.get_cat(sscat['cat_id'])
    return render_template('sscat.html',sscat=sscat,cat=cat)

@app.route('/topic/<int:id>')
def affichetopic(id):
    if request.method == 'GET':
        pass
    elif resquest.method == 'POST':
        pass
    topic = models.Topic.get_topic(id)
    if(not topic):
        abort(404)
    topic['com'] = models.Topic.get_coms(id)
    sscat=models.Sous_cat.get_sscat(topic['sscat_id'])
    cat=models.Cat.get_cat(sscat['cat_id'])
    return render_template('topic.html',topic=topic,sscat=sscat,cat=cat)

@app.route('/user/<int:id>')
@deny_access(401)
def afficheuser(id):
    if request.method == 'GET':
        pass
    elif resquest.method == 'POST':
        pass
    user = models.User.get_user(id)
    if(not user):
        abort(404)
    topics = models.User.get_topics(id)
    coms = models.User.get_coms(id)
    return render_template('user.html',user=user,topics=topics,coms=coms)

@app.route('/members')
def afficheallusers():
    users = models.User.get_all_users()
    return render_template('members.html',users=users)




# -------------------------------------------- ADD CONTENT ------------------------------------------------ #




@app.route('/add_category', methods=['GET', 'POST'])
def addcat():
    try:
        return add_content('category')
    except TypeError as e:
        print "{message}".format(message=e.message)
        abort(404)

@app.route('/add_subcategory/<int:cat_id>', methods=['GET', 'POST'])
def addsubcat(cat_id):
    try:
        return add_content('subcategory',cat_id)
    except TypeError as e:
        print "{message}".format(message=e.message)
        abort(404)

@app.route('/add_topic/<int:sscat_id>', methods=['GET', 'POST'])
@deny_access(401)
def addtopic(sscat_id):
    try:
        return add_content('topic',sscat_id,1)
    except TypeError as e:
        print "{message}".format(message=e.message)
        abort(404)

@app.route('/add_com/<int:topic_id>', methods=['GET', 'POST'])
@deny_access(401)
def addcom(topic_id):
    try:
        return add_content('comment',topic_id, 1)
    except TypeError as e:
        print "{message}".format(message=e.message)
        abort(404)

def add_content(type, container_id=None, user_id=None):
    champs={}
    if type == 'comment':
        champs['requis'] = ['content']
        container = models.Topic.get_topic(container_id)['titre']
        back = url_for('affichetopic', id=container_id)
    elif type == 'topic':
        champs['requis'] = ['title','content']
        container = models.Sous_cat.get_sscat(container_id)['titre']
        back = url_for('affichesscat', id=container_id)
    elif type == 'subcategory':
        champs['requis'] = ['title']
        container = models.Cat.get_cat(container_id)['titre']
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
            if type == 'comment':
                models.Com.insert(container_id,user_id, result['form']['title'], nl2br(result['form']['content']))
            elif type == 'topic':
                models.Topic.insert(container_id,user_id, result['form']['title'], nl2br(result['form']['content']))
            elif type == 'subcategory':
                if existing_sscat(container,result['form']['title'],result['errors']):
                    return render_template('add_content.html',form=result['form'], errors=result['errors'], type=type, container=container, back=back)
                models.Sous_cat.insert(result['form']['title'],container_id)
            else:
                if existing_cat(result['form']['title'],result['errors']):
                    return render_template('add_content.html',form=result['form'], errors=result['errors'], type=type, container=container, back=back)
                models.Cat.insert(result['form']['title'])
            return redirect(back)
        else:
            return render_template('add_content.html',form=result['form'], errors=result['errors'], type=type, container=container, back=back)
add_content=deny_access(403)(add_content)




# -------------------------------------------- EDIT/DELETE CONTENT ------------------------------------------------ #




@app.route('/edit_category/<int:cat_id>', methods=['GET', 'POST'])
def editcat(cat_id):
    cat = models.Cat.get_cat(cat_id)
    if(cat):
        return edit_content(cat,'category')
    print "Category {} not found".format(cat_id)
    abort(404)

@app.route('/edit_subcategory/<int:sscat_id>', methods=['GET', 'POST'])
def editsubcat(sscat_id):
    sscat = models.Sous_cat.get_sscat(sscat_id)
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
            if type == 'comment':
                models.Com.edit(this['id'],result['form']['title'],nl2br(result['form']['content']))
            elif type == 'topic':
                models.Topic.edit(this['id'],nl2br(result['form']['content']))
            elif type == 'subcategory':
                cat_titre=models.Cat.get_cat(this['cat_id'])['titre']
                if existing_sscat(cat_titre,result['form']['title'],result['errors']):
                    return render_template('manage_content.html',form=result['form'], errors=result['errors'], type=type, this=this, back=back)
                models.Sous_cat.edit(this['id'],result['form']['title'])
            else:
                if existing_cat(result['form']['title'],result['errors']):
                    return render_template('manage_content.html',form=result['form'], errors=result['errors'], type=type, this=this, back=back)
                models.Cat.edit(this['id'],result['form']['title'])
            return redirect(back)
        else:
            return render_template('manage_content.html',form=result['form'], errors=result['errors'], type=type, this=this, back=back)
edit_content=deny_access(403)(edit_content)

@app.route('/delete')
@deny_access(403)
def delete():
    type = request.args['type']
    id = request.args['id']
    if(type == 'comment'):
        back=models.Com.get_com(id)['topic_id']
        models.Com.delete(id)
        return redirect(url_for('affichetopic', id=back))
    elif(type == 'topic'):
        back=models.Topic.get_topic(id)['sscat_id']
        models.Topic.delete(id)
        return redirect(url_for('affichesscat', id=back))
    elif(type == 'subcategory'):
        back=models.Sous_cat.get_sscat(id)['cat_id']
        models.Sous_cat.delete(id)
        return redirect(url_for('affichecat', id=back))
    else:
        models.Cat.delete(id)
        return redirect('/')




# -------------------------------------------- VALIDITY TESTS ------------------------------------------------ #




def validate(form, champs):
    result = {'valid': True, 'form': form, 'errors': {}}

    if champs.get('requis',None):
        for champ in champs['requis']:
            result['valid'] = champ_requis(form, champ, result['errors']) and result['valid']
    if not result['valid']:
        return result

    if champs.get('pseudo',None):
        for champ in champs['pseudo']:
            result['valid'] = (not existing_username(form[champ], result['errors'])) and result['valid']

    if champs.get('email',None):
        for champ in champs['email']:
            result['valid'] = valid_email(form[champ], result['errors']) and (not existing_email(form[champ], result['errors'])) and result['valid']

    champ = champs.get('pwd', None)
    if champ:
        pwd1,pwd2 = form[champ[0]], form[champ[1]]
        result['valid'] = password_check(pwd1,pwd2, result['errors']) and result['valid']

    champ = champs.get('date', None)
    if champ and form[champ]:
        result['valid'] = valid_date_format(form[champ], result['errors']) and result['valid']

    if champs.get('check',None):
        for champ in champs['check']:
            result['valid'] = checked(form, champ, result['errors']) and result['valid']
    
    if champs.get('name',None):
        for champ in champs['name']:
            if form[champ]:
                result['valid'] = valid_name(form, champ, result['errors']) and result['valid']
    
    return result


def champ_requis(form, champ, errors):
    if form[champ] == '':
        errors[champ] = 'A {} is required'.format(champ)
        return False
    else:
        return True

def existing_sscat(cat_titre, sscat_titre, errors):
    if(models.Sous_cat.get_sscat_id(sscat_titre, cat_titre)):
        errors['title'] = 'This name is already used in {}'.format(cat_titre)
        return True
    return False

def existing_cat(cat_titre, errors):
    if models.Cat.get_cat_id(cat_titre):
        errors['title'] = 'A category with this name already exists'
        return True
    return False

def existing_username(username, errors):
    if models.User.get_user_id(username):
        errors['pseudo'] = 'This username is already used'
        return True
    return False

def existing_email(email, errors):
    if models.User.get_user_id_by_mail(email):
        errors['email'] = 'This email is already used'
        return True
    return False

def valid_email(email, errors):
    if not validate_email('example@example.com'):
        errors['email'] = 'This email is not is a valid format'
        return False
    #if not validate_email('example@example.com',verify=True):
    #    errors['email'] = 'This email does not exists'
    #    return False
    return True

def password_check(pwd,pwdbis,errors):
    """
    Verify the strength of 'password'
    A password is considered strong if:
        8 characters length or more
        at least 1 digit or symbol
        at least 1 uppercase or lowercase letter
    """
    length=len(pwd)
    if length<8 or length>50:
        errors['password'] = 'Your password must contain between 8 and 50 letters'
        return False

    # searching for digits or symbols
    if not (re.search(r"\d", pwd) or re.search(r"\W", pwd)):
        errors['password'] = 'Your password must contain at least one digit or symbol'
        return False

    if not re.search(r"[a-zA-Z]", pwd):
        errors['password'] = 'Your password must contain at least a letter'
        return False

    if pwd != pwdbis:
        errors['passwordbis'] = 'Must be identical to your password'
        return False
    return True

def identify(pseudo, pwd, errors):
    id=models.User.get_user_id(pseudo)
    if id:
        user=models.User.get_user(id)
        if(hashpw(pwd.encode('UTF_8'),user['password'].encode('UTF_8')).decode() == user['password']):
            return user
    errors['combine'] = 'This username/password combinaison does not exists'
    return None

def valid_date_format(date, errors):
    try:
        datetime.datetime.strptime(date, '%m/%d/%Y')
        return True
    except ValueError:
        errors['bday'] = 'Incorrect date format, should be MM/DD/YYYY'
        return False

def valid_name(form,champ, errors):
    if re.match("[A-Za-z-]+$",form[champ], re.LOCALE) and re.search(r"[a-zA-Z]", form[champ], re.LOCALE):
        return True
    errors[champ] = 'Invalid name format, please use only letters and -'
    return False

def checked(form,checkbox, errors):
    if form.get(checkbox,None):
        return True
    errors[checkbox] = 'Not checked'
    return False

def nl2br(string, is_xhtml= False):
    if is_xhtml:
        return string.replace('\n','<br />\n')
    else :
        return string.replace('\n','<br>\n')