## Assignment credits: collaboration with Justine Brakefield
## code modified from "Get It Done!"

from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:pigeon@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '$uperS3cr3t!'


class Blog(db.Model):

    post_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    content = db.Column(db.String(10000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, name, content, owner):
        self.name = name
        self.content = content
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['show_blog', 'signup', 'login', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/',methods=['POST', 'GET'])
def index():
    return redirect('/blog')

@app.route('/blog', methods=['POST', 'GET'])
def show_blog():
    posts = Blog.query.all()
    blog_id = request.args.get('id')
    blog_post = Blog.query.filter_by(post_id=blog_id).first()
    if blog_id:
        return render_template('blog_post.html',post=blog_post)
    else:
        return render_template('blog.html', title="Blogz", posts=posts)


@app.route('/newpost', methods=['GET','POST'])
def post_new():
    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        post_name = request.form['name']
        post_content = request.form['content']
        new_post = Blog(name = post_name, content = post_content, owner = owner)

        #check if name and content contain only whitespace 
        if not post_name.strip():
            flash("You must give your post a name.")
            return render_template('new_post.html')
        if not post_content.strip():
            flash("You must enter content for your post.")
            return render_template('new_post.html')

        db.session.add(new_post)
        db.session.commit()
        new_id = str(new_post.post_id)
        return redirect('/blog?id=' + new_id)

    return render_template('new_post.html',title="New Post")

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username = username).first()

        if user and user.password == password:
            session['username'] = username
            flash("You are now logged in!")
            return redirect('/newpost')
        elif not user:
            flash('User does not exist', 'error')
            return render_template('login.html')
        elif user.password != password:
            flash('Password is incorrect','error')
            return render_template('login.html')

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        # TODO - validate user's data

        existing_user = User.query.filter_by(username = username).first()

        if not username or not password or not verify:
            flash('Please complete all fields', 'error')
            return render_template('signup.html')
        elif existing_user:
            flash('That user already exists', 'error')
            return render_template('signup.html')
        elif len(password) < 3 or  len(username) < 3:
            flash('usernames and passwords must be at least 3 characters long', 'error')
            return render_template('signup.html')
        elif password != verify:
            flash('Passwords must match', 'error')
            return render_template('signup.html')
        elif not existing_user and password == verify:
            new_user = User(username = username, password = password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
    return render_template('signup.html')

@app.route('/logout')
def logout():
    owner = User.query.filter_by(username=session['username']).first()
    if owner:
        del session['username']
        return redirect('/blog')
    else:
        flash('You are not logged in!', 'error')
        return redirect('/login')

if __name__ == '__main__':
    app.run()
