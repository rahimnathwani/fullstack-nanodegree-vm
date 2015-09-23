from datetime import datetime
from random import sample, choice
import string
from flask import Flask, render_template, request, redirect
from flask.ext.sqlalchemy import SQLAlchemy
from requests.utils import quote
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/catalog.db'
db = SQLAlchemy(app)

GITHUB_CLIENT_ID = '5c17c850fac858500c71'
GITHUB_CLIENT_SECRET = 'c07f87f7074a8cc4e0b5ed5dc138e03b50a464b0'
OAUTH_REDIRECT_URI = "http://localhost:5000/oauth_callback"
REDIRECT_URI = "http://localhost:5000/"



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

@app.route('/')
def catalog_view():
    categories = Category.query.all()
    print 'a'
    category_id = request.args.get('cat', '')
    if category_id == '':
        items = Item.query.order_by(Item.created.desc()).all()
        print 'b'
    else:
        category = Category.query.get(category_id)
        items = Item.query.filter_by(category=category).order_by(Item.created.desc()).all()
    print len(items)

    return render_template('catalog.html',
                           items=items,
                           categories=categories)

@app.route('/add', methods=['GET','POST'])
def add_item():
    if request.method == 'POST':
        # process the new item form
        return "processing form..."
    else:
        # get the list of categories for the drop down
        categories = Category.query.all()
        # show form for new item
        return render_template('add_item_form.html',
                               categories=categories)


@app.route('/login')
def login():
    return redirect("https://github.com/login/oauth/authorize?client_id="
                    + GITHUB_CLIENT_ID
                    + "&redirect_uri=" + quote(OAUTH_REDIRECT_URI),
                    code=302)


@app.route('/oauth_callback')
def oauth_callback():
    code = request.args.get('code', '')
    if code == '':
        return "something went wrong"
    # POST to https://github.com/login/oauth/access_token
    # Instructions at https://developer.github.com/v3/oauth/
    payload = {'client_id': GITHUB_CLIENT_ID,
               'client_secret': GITHUB_CLIENT_SECRET,
               'code': code,
               'redirect_uri': OAUTH_REDIRECT_URI
               }
    headers = {'Accept': 'application/json'}
    r = requests.post("https://github.com/login/oauth/access_token",
                      data=payload,
                      headers=headers)
    print r.status_code
    return (r.text)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
