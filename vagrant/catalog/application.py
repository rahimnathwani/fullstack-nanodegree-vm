from datetime import datetime
from random import sample, choice
import string, json
from flask import Flask, render_template, request, redirect, session, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from requests.utils import quote
import requests

app = Flask(__name__)
# Using sqlite for now, to allow easier installation
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/catalog.db'
# secret key used for signing client cookies
app.secret_key = '\xdf\x90u[\xd9\x84o8$\x08u\x8c\xc6Fx\x9c\x9c2G.K\xf9\x11{'
# Using an ORM, as we don't want to write SQL by hand
db = SQLAlchemy(app)

# Configuration constants
GITHUB_CLIENT_ID = '5c17c850fac858500c71'
GITHUB_CLIENT_SECRET = 'c07f87f7074a8cc4e0b5ed5dc138e03b50a464b0'
OAUTH_REDIRECT_URI = "http://localhost:5000/oauth_callback"
HOME_URI = "http://localhost:5000/"


def random_string(length=20):
    return ''.join(choice(string.ascii_lowercase) for _ in range(length))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return u'<User %r>' % self.name


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User',
                           backref=db.backref('items', lazy='dynamic'))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category',
                               backref=db.backref('items', lazy='dynamic'))
    created = db.Column(db.DateTime)

    def __init__(self, title, description, category, user):
        self.title = title
        self.description = description
        self.category = category
        self.user = user
        self.created = datetime.utcnow()

    def __repr__(self):
        return u'<Item %r>' % self.title


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Category %r>' % self.name


def create_sample_data():
    db.create_all()
    for name in ['jim', 'bob', 'james']:
        db.session.add(User(name))
        db.session.commit()
    for title in ['Alpha', 'Betta', 'Gamma']:
        db.session.add(Category(title))
        db.session.commit()
    for title, desc in [('Snowboarding', 'fun fun fun'),
                        ('Skiing', 'less fun')]:
        db.session.add(Item(title,
                            desc,
                            sample(Category.query.all(), 1)[0],
                            sample(User.query.all(), 1)[0]))
        db.session.commit()
        
def logged_in_user():
    if 'username' in session:
        return User.query.filter_by(name=session['username']).first()
    else:
        return None

@app.route('/')
def catalog_view():
    categories = Category.query.all()
    category_id = request.args.get('cat', '')
    item_id = request.args.get('item', '')
    if item_id == '':
        item = ''
        item_owner = False
    else:
        item = Item.query.get(item_id)
        item_owner = True if item.user == logged_in_user() else False
    if category_id == '':
        items = Item.query.order_by(Item.created.desc()).all()
    else:
        category = Category.query.get(category_id)
        items = Item.query.filter_by(category=category).order_by(Item.created.desc()).all()

    return render_template('catalog.html',
                           item=item,
                           item_owner=item_owner,
                           items=items,
                           categories=categories,
                           username = session['username'] if 'username' in session else 'no one :(')

@app.route('/add', methods=['GET','POST'])
def add_item():
    # Only logged-in users can add items
    if logged_in_user() is None:
        return redirect(url_for('login'))
    # Check if this is a form submission, or whether they are just GETting the blank form
    if request.method == 'POST':
        title = request.form['item_name']
        description = request.form['description']
        category = Category.query.get(int(request.form['category']))
        a = Item(title, description, category, logged_in_user())
        db.session.add(a)
        db.session.commit()
        return redirect(HOME_URI)
    else:
        # get the list of categories for the drop down
        categories = Category.query.all()
        # show form for new item
        return render_template('add_item_form.html',
                               categories=categories)

@app.route('/edit', methods=['POST'])
def edit_item():
    # Check if the user owns the item
    item = Item.query.get(request.form['item_id'])
    if logged_in_user() != item.user:
        return redirect(HOME_URI)
    # No need to check the request type, as the method only accepts POST
    item.title = request.form['item_name']
    item.description = request.form['description']
    item.category = Category.query.get(int(request.form['category']))
    db.session.commit()
    return redirect(HOME_URI)


@app.route('/delete', methods=['POST'])
def delete_item():
    # Check if the user owns the item
    item = Item.query.get(request.form['item_id'])
    if logged_in_user() != item.user:
        return redirect(HOME_URI)
    db.session.delete(item)
    db.session.commit()
    return redirect(HOME_URI)


@app.route('/login')
def login():
    return redirect("https://github.com/login/oauth/authorize?client_id="
                    + GITHUB_CLIENT_ID
                    + "&redirect_uri=" + quote(OAUTH_REDIRECT_URI),
                    code=302)
                    
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(HOME_URI)


@app.route('/oauth_callback')
def oauth_callback():
    # After the user agrees, GitHub should give us a code
    code = request.args.get('code', '')
    if code == '':
        return "something went wrong"

    # We can swap the code for an access token
    payload = {'client_id': GITHUB_CLIENT_ID,
               'client_secret': GITHUB_CLIENT_SECRET,
               'code': code,
               'redirect_uri': OAUTH_REDIRECT_URI
               }
    headers = {'Accept': 'application/json'}
    r = requests.post("https://github.com/login/oauth/access_token",
                      data=payload,
                      headers=headers)
    access_token = json.loads(r.text)['access_token']

    # We can use the access token to access the user's GitHub profile.
    # Get the user's GitHub name.  It is unique and immutable, so we won't bother to get the user's numeric ID.
    headers = {'Authorization': "token " + access_token}
    r = requests.get("https://api.github.com/user", headers=headers)
    github_login = json.loads(r.text)['login']

    # Check if the user has used our site before, and create an account if she hasn't
    current_user = User.query.filter_by(name=github_login).first()
    if current_user is None:
        current_user = User(github_login)
        db.session.add(current_user)
        db.session.commit()
    
    # Log in the user by adding/replacing the username in the session cookie
    session.pop('username', None)
    session['username'] = current_user.name
    return redirect(HOME_URI)

@app.route('/catalog.json')
def all_as_json():
    stuff_to_return = {}
    categories = Category.query.all()
    for category in categories:
        category_items = {}
        for item in category.items:
            category_items[item.id] = {'name': item.title,
                                      'description': item.description}
        category_dict = {'category_name': category.name,
                         'items': category_items}
        stuff_to_return[category.id] = category_dict
    return json.dumps(stuff_to_return)
        
              



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
