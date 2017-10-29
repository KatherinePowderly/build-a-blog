from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:beproductive@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

app.secret_key = 'someSecretString'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.route('/')
def index():

    users = User.query.all()
    return render_template('index.html', users=users)


@app.before_request
def require_login():
    allowed_routes = ['login', 'post', 'signup', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')



@app.route('/login', methods=['POST', 'GET'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['username'] = username
            flash("Logged In", 'logged_in')
            print(session)
            return redirect('/newpost')
        elif user and not user.password == password:
            flash('Password Error', 'password_error')
            print(session)
            return redirect('/login')

        else:
            flash('Username Error', 'username_error')
            return redirect('/login')

    return render_template('login.html')





@app.route('/signup', methods=['POST', 'GET'])
def signup():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        username_error = ""
        password_error = ""
        verify_error = ""

        existing_user = User.query.filter_by(username=username).first()

        if not username:
            username_error = "Error: Field cannot be left empty"
            username = ""
        else:
            username_len = len(username)
            if  username_len < 3:
                username_error = "Error: Username must contain 3 or more characters"
                username = ""

        if not verify:
            verify_error = "Error: Field cannot be left empty"
            verify = ""
        else:
            if verify != password:
                verify_error = "Error: Passwords must match"
                verify = ""

        if not password:
            password_error = "Error: Field cannot be left empty"
            password = ""
        else:
            password_len = len(password)
            if  password_len < 3:
                password_error = "Error: Username must contain 3 or more characters"
                password = ""

        if not existing_user and username_error or password_error or verify_error:
            return render_template ('signup.html', username=username, username_error=username_error, password_error=password_error, verify_error=verify_error)

        elif not existing_user and not username_error and not password_error and not verify_error:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            flash('Error: Duplicate username', 'duplicate_username')
            return redirect('/signup')

    return render_template('signup.html')






@app.route('/blog', methods=['POST', 'GET'])
def show_posts():

    #Single
    if request.method == 'GET' and request.args.get('id'):
        blog_id = request.args.get('id')
        blog = Blog.query.get(blog_id)
        user_id = blog.owner_id
        user = User.query.get(user_id)
        return render_template('singleBlog.html', title='Blogz', user=user, blog=blog)

    #All User Blogs
    if request.method == 'GET' and request.args.get('userID'):
        user_id = request.args.get('userID')
        user = User.query.get(user_id)
        user_blogs = Blog.query.filter_by(owner_id=user_id).all()
        return render_template('singleUser.html', title='Blogz', user=user, user_blogs=user_blogs)

    #All
    if request.method == 'GET' or request.method == 'POST':
        blogs = Blog.query.all()
        return render_template('all_blogs.html', title='Blogz', blogs=blogs)







@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    if request.method == 'GET':
        return render_template('newpost.html', title="Blogz")

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        title_error = ""
        body_error = ""

        owner = User.query.filter_by(username=session['username']).first()
        error = "Error: Field cannot be left empty"

        if not blog_title:
            title_error = error
            return render_template('newpost.html', title="Build A Blog!", title_error=title_error, blog_body=blog_body)

        if not blog_body:
            body_error = error
            return render_template('newpost.html', title="Build A Blog!", body_error=body_error, blog_title=blog_title)




        if not title_error and not body_error:
            newpost = Blog(blog_title, blog_body, owner)
            db.session.add(newpost)
            db.session.commit()
            blog_id = newpost.id
            return redirect("/blog?id={}".format(blog_id))


        

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

if __name__ == '__main__':
    app.run()