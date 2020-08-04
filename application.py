from flask import Flask, render_template, request, flash, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import json
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import UserMixin, LoginManager, current_user, login_user, logout_user
from flask_security import Security, SQLAlchemyUserDatastore, login_required, \
    UserMixin, RoleMixin, LoginForm, url_for_security
from flask_security.utils import hash_password
  

with open('config.json', 'r') as c:
    params = json.load(c)["params"]

local_server = params['local_server']
application = app = Flask(__name__)
app.secret_key = 'ajj-patel-15'
app.config['UPLOAD_FOLDER'] = params['p1_upload_loc']
app.config['SECURITY_PASSWORD_SALT'] = 'thisisasecretsalt'
# app.config['SECURITY_LOGIN_USER_TEMPLATE'] = 'security/login.html'
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail-user'],
    MAIL_PASSWORD=params['gmail-password']
)
mail = Mail(app)
if (local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri'] # "mysql://root:@localhost/flask_tut1"
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db = SQLAlchemy(app)

##########################

roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id')))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    # name = db.Column(db.String(20))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(255))
    is_admin = db.Column(db.Boolean, default = False)
    active = db.Column(db.Boolean)
    confirmed_at = db.Column(db.DateTime)
    roles = db.relationship(
        'Role', 
        secondary=roles_users, 
        backref=db.backref('users', lazy='dynamic')
    )

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    description = db.Column(db.String(255))

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        user_datastore.create_user(
            email=request.form.get('email'),
            password=hash_password(request.form.get('password'))
        )
        db.session.commit()

        return redirect(url_for('projects_add_new'))

    return render_template('register.html', params=params)

# login = LoginManager(app)
# @login.user_loader
# def load_user(user_id):
#     return User.query.get(user_id)

class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(12), nullable=False)
    msg = db.Column(db.String(120), nullable=False)
    # date = db.Column(db.String(12), nullable=True)
    email = db.Column(db.String(20), nullable=False)


class Blogs(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(25), nullable=False)
    content = db.Column(db.Text)
    date = db.Column(db.String(12), nullable=True)
    # email = db.Column(db.String(20), nullable=False)
    #for editor



class Projects(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.String(1000), nullable=False)
    name = db.Column(db.String(25), nullable=False)
    program = db.Column(db.String(20), nullable=False)
    year = db.Column(db.String(20), nullable=False)
    step1 = db.Column(db.String(100), nullable=False)
    step2 = db.Column(db.String(100), nullable=False)
    step3 = db.Column(db.String(100), nullable=False)
    step4 = db.Column(db.String(100), nullable=False)
    step1content = db.Column(db.String(250), nullable=False)
    step2content = db.Column(db.String(250), nullable=False)
    step3content = db.Column(db.String(250), nullable=False)
    step4content = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(300), nullable=True)
    is_approved = db.Column(db.Boolean, default = False)
    # live_demo = db.Column(db.Boolean, default = False)
    



class MyModelView(ModelView):
    def is_accessible(self):
        if current_user.is_admin:
            return current_user.is_authenticated
        else:
            return abort(404)
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

class MyAdminIndexView(AdminIndexView):
    pass
    # def is_accessible(self):
    #     if current_user.is_admin:
    #         return current_user.is_authenticated
    #     else:
    #         return abort(404)




admin = Admin(app, index_view = MyAdminIndexView(), template_mode='bootstrap3')
admin.add_view(MyModelView(Projects,db.session))
admin.add_view(MyModelView(User, db.session))
# user_datastore.create_user(
#     email = 'admin@iitgn.ac.in',
#     password = 'projects_admin',
#     is_admin = True
# )
# db.session.commit()

@app.route("/")
def home():
    return render_template('index.html', params=params)

# @app.route("/login")
# def login():
#     user = User.query.get(1)
#     login_user(user)
#     return "logged in !!!"

@app.route("/about")
def about():
    return render_template('about.html', params=params)


#dummy data
posts = [
    {
        'heading': 'Trending Blogs',
        'author' : 'Reuben Shibu',
        'title': 'Blog Post 1',
        'content': 'First post content Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus posuere orci turpis, vitae tempor urna fringilla id. Proin vestibulum augue a viverra bibendum. Sed congue malesuada dolor vitae imperdiet. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Ut vehicula mollis magna, at vulputate erat ullamcorper eu. Sed placerat lacinia elit nec finibus. Morbi posuere in ligula a hendrerit. Integer sed felis faucibus, porta nulla ut, bibendum dolor. Praesent imperdiet lorem non facilisis tincidunt.',
        'date_posted': 'Nov 20, 2019'
    },
    {
        'author' : 'John Doe',
        'title': 'Blog Post 2',
        'content': 'Second post content Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus posuere orci turpis, vitae tempor urna fringilla id. Proin vestibulum augue a viverra bibendum. Sed congue malesuada dolor vitae imperdiet. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Ut vehicula mollis magna, at vulputate erat ullamcorper eu. Sed placerat lacinia elit nec finibus. Morbi posuere in ligula a hendrerit. Integer sed felis faucibus, porta nulla ut, bibendum dolor. Praesent imperdiet lorem non facilisis tincidunt.',
        'date_posted': 'Nov 20, 2020'
    },
    {
        'author' : 'Aditya Shekhar',
        'title': 'Blog Post 3',
        'content': 'Third post content Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus posuere orci turpis, vitae tempor urna fringilla id. Proin vestibulum augue a viverra bibendum. Sed congue malesuada dolor vitae imperdiet. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Ut vehicula mollis magna, at vulputate erat ullamcorper eu. Sed placerat lacinia elit nec finibus. Morbi posuere in ligula a hendrerit. Integer sed felis faucibus, porta nulla ut, bibendum dolor. Praesent imperdiet lorem non facilisis tincidunt.',
        'date_posted': 'Nov 21, 2020'
    },
    {
        'heading': 'Technology',
        'author' : 'Mihir Chauhan',
        'title': 'Tech Blog Post 1',
        'content': 'First post content Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus posuere orci turpis, vitae tempor urna fringilla id. Proin vestibulum augue a viverra bibendum. Sed congue malesuada dolor vitae imperdiet. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Ut vehicula mollis magna, at vulputate erat ullamcorper eu. Sed placerat lacinia elit nec finibus. Morbi posuere in ligula a hendrerit. Integer sed felis faucibus, porta nulla ut, bibendum dolor. Praesent imperdiet lorem non facilisis tincidunt.',
        'date_posted': 'Nov 20, 2019'
    },
    {
        'author' : 'Adolf Hitler',
        'title': 'Tech Blog Post 2',
        'content': 'Second post content Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus posuere orci turpis, vitae tempor urna fringilla id. Proin vestibulum augue a viverra bibendum. Sed congue malesuada dolor vitae imperdiet. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Ut vehicula mollis magna, at vulputate erat ullamcorper eu. Sed placerat lacinia elit nec finibus. Morbi posuere in ligula a hendrerit. Integer sed felis faucibus, porta nulla ut, bibendum dolor. Praesent imperdiet lorem non facilisis tincidunt.',
        'date_posted': 'Nov 20, 2020'
    },
    {
        'author' : 'Mihir Bin Laden',
        'title': 'Tech Blog Post 3',
        'content': 'Third post content. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus posuere orci turpis, vitae tempor urna fringilla id. Proin vestibulum augue a viverra bibendum. Sed congue malesuada dolor vitae imperdiet. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Ut vehicula mollis magna, at vulputate erat ullamcorper eu. Sed placerat lacinia elit nec finibus. Morbi posuere in ligula a hendrerit. Integer sed felis faucibus, porta nulla ut, bibendum dolor. Praesent imperdiet lorem non facilisis tincidunt.',
        'date_posted': 'Sep 11, 2001'
    }
]

@app.route("/blogs", methods=['GET'])
def blogs():
    blogs_details = Blogs.query.filter_by().all()[0:params['no_of_posts']]
    return render_template('blogs.html', params=params, blogs_details=blogs_details, posts = posts)



@app.route("/blogs/add_new", methods=['GET', 'POST'])
@login_required
def blog_add_new():
    if (request.method == "POST"):
        title = request.form.get("display_name")
        content = request.form.get("about")
        entry = Blogs(title=title,  content=content, date=datetime.now())
        db.session.add(entry)
        db.session.commit()
        flash('Submited Successfully!', 'info')
    return render_template('blog_add.html', params=params)

#display writen blog
@app.route("/blogs/display/<int:sno>")
def display(sno):
    data=Blogs.query.get(sno)
    return render_template('display_written_blog.html',data= data.content)


@app.route("/projects", methods=['GET'])
def projects():
    details = Projects.query.filter_by(is_approved=True).all()
    return render_template('projects.html', params=params, details=details)


@app.route("/projects/title/<string:post_title>", methods=['GET'])
def projects_details(post_title):
    details = Projects.query.filter_by(title=post_title).first()
    return render_template('post.html', params=params, details=details)


@app.route("/projects/title/Stock Price Prediction/Demo", methods=['GET','POST'])
def p1_project_demo():
    post_title = 'Stock Price Prediction'
    details = Projects.query.filter_by(title=post_title).first()
    if request.method == 'POST':
        f = request.files['file1']
        filename = secure_filename(f.filename)
        if filename[len(filename)-4:] == '.csv':
            demo_path = os.path.join('static', 'p1_stock_price')
            images = os.listdir(demo_path)
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], 'test.csv'))
            flash('Uploaded Successfully!', 'info')
            render_template('p1_stock_price.html', params=params, details=details, images=images)
            from static.p1_stock_price.train_model import train_model
            train_model(os.path.join('static', 'p1_stock_price', 'test.csv'),150)
            # test_predict(150)
            return render_template('p1_stock_price.html', params=params, details=details, images=images)
        else:
            flash('Please Upload a valid file!', 'info')
            return render_template('p1_stock_price.html', params=params, details=details)
    else:
        return render_template('p1_stock_price.html', params=params, details=details)


@app.route("/projects/title/Write in Air/Demo", methods=['GET', 'POST'])
def p2_project_demo():
    post_title = 'Write in Air'
    details = Projects.query.filter_by(title=post_title).first()
    if request.method == 'POST':
        from static.p2_write_in_air.track3 import track
        output = track()
        flash(output, 'info')
        return render_template('p2_write_in_air.html', params=params, details=details)
    return render_template('p2_write_in_air.html', params=params, details=details)

# @app.route("/post/<string:post_slug>", methods=['GET'])
# def post_route(post_slug):
#     post = Post.query.filter_by(slug=post_slug).first()
#     return render_template('post.html', params=params, post=post)


# @app.route("/projects/title/<string:post_title>/Demo", methods=['GET', 'POST'])
# def uploader():
#     if request.method == 'POST':
#         f = request.files['file1']
#         f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
#         return render_template('demo.html', params=params)

@app.context_processor
def login_context():
    return {
        'url_for_security': url_for_security,
        'login_user_form': LoginForm(),
    }

@app.route("/projects/add_new", methods=['GET', 'POST'])
@login_required
def projects_add_new():
    if (request.method == 'POST'):
        title = request.form.get('title')
        content = request.form.get('content')
        step1 = request.form.get('step1')
        step2 = request.form.get('step2')
        step3 = request.form.get('step3')
        step4 = request.form.get('step4')
        step1content = request.form.get('step1content')
        step2content = request.form.get('step2content')
        step3content = request.form.get('step3content')
        step4content = request.form.get('step4content')
        name = request.form.get('name')
        program = request.form.get('program')
        year = request.form.get('year')
        entry = Projects(title=title, content=content, step1=step1, step2=step2, step3=step3, step4=step4,
                         step1content=step1content, step2content=step2content, step3content=step3content,
                         step4content=step4content, name=name, program=program, year=year, date= datetime.now())
        db.session.add(entry)
        db.session.commit()
        flash('Submited Successfully!', 'info')
    return render_template('project_add.html', params=params)

@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if (request.method == 'POST'):
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = Contacts(name=name, phone=phone, msg=message, email=email)
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message from ' + name,
                          sender=email,
                          recipients=[params['gmail-user']],
                          body=message + "\n" + "Phone number-"+phone
                          )
    return render_template('contact.html', params=params)

if __name__ == '__main__':
    app.run(debug=True)
