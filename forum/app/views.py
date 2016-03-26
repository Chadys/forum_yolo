# coding=utf-8
from flask import Flask, url_for, render_template, request, redirect, abort, Markup, session
from bcrypt import hashpw, gensalt
from functools import wraps
from validate_email import validate_email
import models, ipdb, re, datetime, random
app = Flask(__name__)
app.secret_key = '\x80\x7f\x14\xfe\x0eT\xe6y\xf8\xbff\xe78\xaf\x88~1\xc8\x95\xca&\x1dc!\xe7'
random.seed()



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
            user=models.User.get_user_id(result['form']['pseudo'])
            if user:
                user=models.User.get_user(user)
            if identify(user, result['form']['password'], result['errors']):
                session['id']=user['id']
                session['username']=user['username']
                session['permission']=user['permission']
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
    session.pop('permission', None)
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
            models.User.insert(result['form']['pseudo'],hashpw(result['form']['password'].encode('UTF_8'), gensalt()),result['form']['email'],result['form']['fname'],result['form']['lname'],result['form']['bday'],result['form'].get('sexe',None))
            session['check'] = random.getrandbits(16)
            return redirect(url_for('registration_complete', check = session['check']))
        return render_template('register.html',form=result['form'], errors=result['errors'])

@app.route('/register/success/<int:check>')
def registration_complete(check=None):
    s_check = session.get('check',None)
    if(s_check == check and s_check):
        session.pop('check', None)
        return render_template('registration_complete.html')
    session.pop('check', None)
    abort(400)


def deny_access(perm_mini=None, type=None, hidden=True):
    def decorator(func):
        @wraps(func)
        def wrapper(*args,**kwargs):
            session_id=session.get('id',None)
            if session_id and hidden:
                user_id=None
                if type:
                    if type=='user':
                        user_id=kwargs.get('id')
                    elif type=='topic':
                        user_id=models.Topic.get_topic(kwargs.get('topic_id')).get('user_id')
                    else:
                        user_id=models.Com.get_com(kwargs.get('com_id')).get('user_id')
                if (not perm_mini and not user_id) or session_id == user_id or (perm_mini and session.get('permission') >= perm_mini):
                    return func(*args,**kwargs)
                abort(403)
            return abort(401)
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

def belle_date(date):
    if date:
        if not len(date) > 10:
            return datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%b %d, %Y')
        else:
            return datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S').strftime('%b %d, %Y ; %H:%M:%S')
    return None

def delay(date):
    if date:
        delta = datetime.datetime.now() - datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        delay = str(delta).split(':',2)
        return delay[0]+' hours and '+delay[1]+' minutes ago'
    return None
    
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
            if sscat['der_msg']:
                sscat['der_msg']['date']=delay(sscat['der_msg'].get('date'))
    return render_template('index.html', cats = cats)

@app.route('/category/<int:id>')
def affichecat(id):
    if request.method == 'GET':
        pass
    elif resquest.method == 'POST':
        pass
    cat = models.Cat.get_cat(id)
    if(not cat):
        print "Category {} not found".format(id)
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
        print "Subcategory {} not found".format(id)
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
        print "Topic {} not found".format(id)
        abort(404)
    topic['com'] = models.Topic.get_coms(id)
    sscat=models.Sous_cat.get_sscat(topic['sscat_id'])
    cat=models.Cat.get_cat(sscat['cat_id'])
    return render_template('topic.html',topic=topic,sscat=sscat,cat=cat)

@app.route('/user/<int:id>', methods=['GET', 'POST'])
@deny_access()
def afficheuser(id):
    user = models.User.get_user(id)
    if(not user):
        print "User {} not found".format(id)
        abort(404)
    topics = models.User.get_topics(id)
    coms = models.User.get_coms(id)
    user['date_naiss']= belle_date(user['date_naiss'])
    user['date_creation']= belle_date(user['date_creation'])
    user['date_connection']= belle_date(user['date_connection'])
    #ipdb.set_trace()
    if request.method == 'POST':
        if user['permission'] == 0 or session['permission'] < 15 or (user['permission'] == 15 and user['id'] != session['id']):
            abort(400)
        rang = request.form.get('perm')
        if rang:
            models.User.update_permission(id,rang)
            user['permission']=int(rang)
    return render_template('user.html',user=user,topics=topics,coms=coms)


@app.route('/members')
def afficheallusers():
    users = models.User.get_all_users()
    return render_template('members.html',users=users)




# -------------------------------------------- ADD CONTENT ------------------------------------------------ #




@app.route('/add_category', methods=['GET', 'POST'])
@deny_access(15)
def addcat():
    try:
        return add_content('category')
    except TypeError as e:
        print "{message}".format(message=e.message)
        abort(404)

@app.route('/add_subcategory/<int:cat_id>', methods=['GET', 'POST'])
@deny_access(15)
def addsubcat(cat_id):
    try:
        return add_content('subcategory',cat_id)
    except TypeError as e:
        print "{message}".format(message=e.message)
        abort(404)

@app.route('/add_topic/<int:sscat_id>', methods=['GET', 'POST'])
@deny_access()
def addtopic(sscat_id):
    try:
        return add_content('topic',sscat_id)
    except TypeError as e:
        print "{message}".format(message=e.message)
        abort(404)

@app.route('/add_com/<int:topic_id>', methods=['GET', 'POST'])
@deny_access()
def addcom(topic_id):
    try:
        text = request.args.get('text')
        if text:
            return add_content('comment',topic_id,text+'\n\n')
        return add_content('comment',topic_id)
    except TypeError as e:
        print "{message}".format(message=e.message)
        abort(404)

def add_content(type, container_id=None, text=None):
    champs={}
    form={}
    force_hidden=0
    if type == 'comment':
        champs['requis'] = ['content']
        if text:
            form={'content':text}
        container = models.Topic.get_topic(container_id)['titre']
        back = url_for('affichetopic', id=container_id)
    elif type == 'topic':
        champs['requis'] = ['title','content']
        container = models.Sous_cat.get_sscat(container_id)
        force_hidden=container['hidden']
        container =  container['titre']
        back = url_for('affichesscat', id=container_id)
    elif type == 'subcategory':
        champs['requis'] = ['title']
        container = models.Cat.get_cat(container_id)
        force_hidden=container['hidden']
        container =  container['titre']
        back = url_for('affichecat', id=container_id)
    else:
        champs['requis'] = ['title']
        container = 'the forum'
        back = '/'

    if request.method == 'GET':
        return render_template('add_content.html', form=form, errors={}, type=type, container=container, back=back, hidden=force_hidden,force_hidden=force_hidden)
    else:
        form = request.form
        hidden = 1 if force_hidden or form.get('hidden',None) else 0
        result =  validate(form, champs)
        if result['valid']:
            if type == 'comment':
                models.Com.insert(container_id,session['id'], result['form']['title'], nl2br(result['form']['content']))
            elif type == 'topic':
                models.Topic.insert(container_id,session['id'], result['form']['title'], nl2br(result['form']['content']),hidden)
            elif type == 'subcategory':
                if existing_sscat(container,result['form']['title'],result['errors']):
                    return render_template('add_content.html',form=result['form'], errors=result['errors'], type=type, container=container, back=back, hidden=hidden,force_hidden=force_hidden)
                models.Sous_cat.insert(result['form']['title'],container_id,hidden)
            else:
                if existing_cat(result['form']['title'],result['errors']):
                    return render_template('add_content.html',form=result['form'], errors=result['errors'], type=type, container=container, back=back, hidden=hidden,force_hidden=force_hidden)
                models.Cat.insert(result['form']['title'],hidden)
            return redirect(back)
        else:
            return render_template('add_content.html',form=result['form'], errors=result['errors'], type=type, container=container, back=back, hidden=hidden,force_hidden=force_hidden)




# -------------------------------------------- EDIT/DELETE CONTENT ------------------------------------------------ #




@app.route('/edit_category/<int:cat_id>', methods=['GET', 'POST'])
@deny_access(15)
def editcat(cat_id):
    cat = models.Cat.get_cat(cat_id)
    if(cat):
        return edit_content(cat,'category')
    print "Category {} not found".format(cat_id)
    abort(404)

@app.route('/edit_subcategory/<int:sscat_id>', methods=['GET', 'POST'])
@deny_access(15)
def editsubcat(sscat_id):
    sscat = models.Sous_cat.get_sscat(sscat_id)
    if(sscat):
        return edit_content(sscat,'subcategory')
    print "Subcategory {} not found".format(sscat_id)
    abort(404)

@app.route('/edit_topic/<int:topic_id>', methods=['GET', 'POST'])
@deny_access(10,'topic')
def edittopic(topic_id):
    topic = models.Topic.get_topic(topic_id)
    if(topic):
        return edit_content(topic,'topic')
    print "Topic {} not found".format(topic_id)
    abort(404)

@app.route('/edit_com/<int:com_id>', methods=['GET', 'POST'])
@deny_access(10,'com')
def editcom(com_id):
    com = models.Com.get_com(com_id)
    if(com):
        return edit_content(com,'comment')
    print "Comment {} not found".format(com_id)
    abort(404)

def edit_content(this,type):
    champs={}
    force_hidden=0
    if(type in {'comment', 'topic'}):
        champs['requis'] = ['content']
        form = {'title':this['titre'],'content':nl2br(this['text'],True)}
        if(type == 'comment'):
            back = url_for('affichetopic', id=this['topic_id'])
        else:
            force_hidden=models.Sous_cat.get_sscat(this['sscat_id'])['hidden']
            back = url_for('affichetopic', id=this['id'])
    else:
        champs['requis'] = ['title']
        form = {'title':this['titre']}
        if(type == 'subcategory'):
            force_hidden=models.Cat.get_cat(this['cat_id'])['hidden']
            back = url_for('affichesscat', id=this['id'])
        else:
            back = url_for('affichecat', id=this['id'])

    if request.method == 'GET':
        return render_template('manage_content.html', form=form, errors={}, type=type, this=this, back=back, force_hidden=force_hidden)
    else:
        form = request.form
        hidden = 1 if force_hidden or form.get('hidden',None) else 0
        result =  validate(form, champs)
        if result['valid']:
            if type == 'comment':
                models.Com.edit(this['id'],result['form']['title'],nl2br(result['form']['content']))
            elif type == 'topic':
                models.Topic.edit(this['id'],result['form']['title'],nl2br(result['form']['content']),hidden)
            elif type == 'subcategory':
                cat_titre=models.Cat.get_cat(this['cat_id'])['titre']
                if result['form']['title'] != this['titre'] and existing_sscat(cat_titre,result['form']['title'],result['errors']):
                    return render_template('manage_content.html',form=result['form'], errors=result['errors'], type=type, this=this, back=back, force_hidden=force_hidden)
                models.Sous_cat.edit(this['id'],result['form']['title'],hidden)
            else:
                if result['form']['title'] != this['titre'] and existing_cat(result['form']['title'],result['errors']):
                    return render_template('manage_content.html',form=result['form'], errors=result['errors'], type=type, this=this, back=back, force_hidden=force_hidden)
                models.Cat.edit(this['id'],result['form']['title'],hidden)
            return redirect(back)
        else:
            return render_template('manage_content.html',form=result['form'], errors=result['errors'], type=type, this=this, back=back, force_hidden=force_hidden)

@app.route('/delete')
@deny_access()
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
    elif(type == 'category'):
        models.Cat.delete(id)
    else:
        models.User.delete(id)
        if session['id'] == id:
            return redirect('/logout')
    return redirect('/')

@app.route('/moderate')
@deny_access()
def moderate():
    type = request.args['type']
    id = request.args['id']
    modo = request.args['modo']
    if(type == 'comment'):
        back=models.Com.get_com(id)['topic_id']
        models.Com.moderate(id, modo)
        return redirect(url_for('affichetopic', id=back))
    else:
        models.Topic.moderate(id, modo)
        return redirect(url_for('affichetopic', id=id))

@app.route('/edit_user/<int:id>', methods=['GET', 'POST'])
@deny_access(15,'user')
def edituser(id):
    #ipdb.set_trace()
    user = models.User.get_user(id)
    if not user:
        print "User {} not found".format(id)
        abort(404)
    champs={'requis':['pseudo', 'email']}
    edit=1

    if request.method == 'GET':
        bday = user['date_naiss']
        if bday:
            bday = datetime.datetime.strptime(bday, '%Y-%m-%d').strftime('%m/%d/%Y')
        return render_template('register.html', form={'pseudo':user['username'],'email':user['email'],'bday':bday,'sexe':user['sexe'],'fname':user['prenom'],'lname':user['nom']}, errors={}, edit=edit, id=user['id'])
    else:
        form = request.form
        if form['pseudo'] != user['username']:
            champs['pseudo'] = ['pseudo']
        if form['email'] != user['email']:
            champs['email'] = ['email']
        if form['bday']:
            champs['date']='bday'
        if form['fname']:
            champs['name']=['fname']
        if form['lname']:
            if champs.get('name',None):
                champs['name'].append('lname')
            else:
                champs['name']=['lname']
        if form['passwordbis']:
            champs['requis'].append('password')
            champs['pwd']=['passwordbis']
        result =  validate(form, champs)
        if result['form']['passwordbis']:
            result['valid'] = identify(user, result['form']['password'], result['errors'], True) and result['valid']
            password=hashpw(result['form']['passwordbis'].encode('UTF_8'), gensalt())
        else:
            password=None
        if result['valid']:
            models.User.update(id, result['form']['pseudo'],password,result['form']['email'],result['form']['fname'],result['form']['lname'],datetime.datetime.strptime(result['form']['bday'], '%m/%d/%Y').strftime('%Y-%m-%d'),result['form'].get('sexe',None))
            edit=2
        return render_template('register.html',form=result['form'], errors=result['errors'], edit=edit, id=user['id'])

@app.route('/ban/<int:id>')
@deny_access(10)
def ban(id):
    user=models.User.get_user(id)
    if not user:
        print "User {} not found".format(id)
        abort(404)
    if session.get('permission') <= user.get('permission'):
        abort(403)
    if user['permission']:
        new_rang=0
    else:
        new_rang=7
    models.User.update_permission(id,new_rang)
    return redirect(url_for('afficheuser', id=id))




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
            result['valid'] = (not existing_username(form[champ], result['errors'])) and valid_pseudo(form[champ], result['errors']) and result['valid']

    if champs.get('email',None):
        for champ in champs['email']:
            result['valid'] = valid_email(form[champ], result['errors']) and (not existing_email(form[champ], result['errors'])) and result['valid']

    champ = champs.get('pwd', None)
    if champ:
        try:
            pwdbis=champ[1]
        except IndexError:
            pwdbis=None
        result['valid'] = password_check(form,champ[0], result['errors'], pwdbis) and result['valid']

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

def valid_pseudo(pseudo, errors):
    if '(banned)' in pseudo.lower():
        errors['pseudo'] = 'You can''t have "(BANNED)" inside your username'
        return False
    return True

def password_check(form,pwd,errors, pwdbis=None):
    """
    Verify the strength of 'password'
    A password is considered strong if:
        8 characters length or more
        at least 1 digit or symbol
        at least 1 uppercase or lowercase letter
    """
    length=len(form[pwd])
    if length<8 or length>50:
        errors[pwd] = 'Your password must contain between 8 and 50 letters'
        return False

    # searching for digits or symbols
    if not (re.search(r"\d", form[pwd]) or re.search(r"\W", form[pwd])):
        errors[pwd] = 'Your password must contain at least one digit or symbol'
        return False

    if not re.search(r"[a-zA-Z]", form[pwd]):
        errors[pwd] = 'Your password must contain at least a letter'
        return False

    if pwdbis and form[pwd] != form[pwdbis]:
        errors[pwdbis] = 'Must be identical to your password'
        return False
    return True

def identify(user, pwd, errors, edit=False):
    if user:
        if user['permission'] == 0:
            errors['combine'] = '<strong>You have been banned. You won''t be able to log in anymore until you get unbanned</strong>'
            return False
        if hashpw(pwd.encode('UTF_8'),user['password'].encode('UTF_8')).decode() == user['password']:
            return True
    if not edit:
        errors['combine'] = 'This username/password combinaison does not exists'
    else:
        errors['password'] = 'Wrong password'
    return False

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

def nl2br(string, reverse= False):
    if reverse:
        return string.replace('<br>\n','\n')
    else :
        return string.replace('\n','<br>\n')