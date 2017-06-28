from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:pigeon@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    post_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    content = db.Column(db.String(10000))

    def __init__(self, name,content):
        self.name = name
        self.content = content

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
        return render_template('blog.html', title="Build-a-Blog", posts=posts)


@app.route('/newpost', methods=['GET','POST'])
def post_new():
    #establish empty field errors for the sake of my template
    empty_name = ''
    empty_content = ''

    if request.method == 'POST':
        post_name = request.form['name']
        post_content = request.form['content']
        new_post = Blog(name=post_name,content=post_content)

        #check if name and content contain only whitespace 
        if not post_name.strip():
            empty_name = "You must give your post a name."
            return render_template('new_post.html', empty_name=empty_name, empty_content=empty_content)
        if not post_content.strip():
            empty_content = "You must enter content for your post."
            return render_template('new_post.html', empty_name=empty_name, empty_content=empty_content)

        db.session.add(new_post)
        db.session.commit()
        new_id = str(new_post.post_id)
        return redirect('/blog?id=' + new_id)

    return render_template('new_post.html',title="New Post", empty_name=empty_name, empty_content=empty_content)

@app.route('/test')
def test():
    return render_template('blog_post.html')

if __name__ == '__main__':
    app.run()
