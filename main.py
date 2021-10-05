from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
import requests
from datetime import date, datetime
import smtplib


current_year = datetime.now().year
current_month = datetime.now().month
current_date = datetime.now().date()

my_email = "franciselizabeth7221@gmail.com"
my_password = "Danlizz@7"

app = Flask(__name__)

app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


# WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


# Send Email
def send_message(name, email, phone, message):
    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(user=my_email, password=my_password)
        connection.sendmail(to_addrs=my_email, from_addr=my_email,
                            msg=f"Subject: Blog Message\n\n Name: {name}\n\n"
                                f"Email: {email}\n\n Phone: {phone} \n\n Message: {message}")


# Home
@app.route('/')
@app.route('/index.html')
def home():
    # blog_url = "https://api.npoint.io/76aa84646074fa3edf51"
    # response = requests.get(url=blog_url)
    # blog_data = response.json()
    blog_data = BlogPost.query.all()
    return render_template("index.html", posts=blog_data, year=current_year, month=current_month, date=current_date)


# Blog
@app.route('/post.html/<int:index>', methods=['GET'])
def blog(index):
    # selected_post = None
    # blog_url = "https://api.npoint.io/76aa84646074fa3edf51"
    # response = requests.get(url=blog_url)
    # posts = response.json()
    # for blog_post in posts:
    #     if blog_post["blogid"] == index:
    #         selected_post = blog_post
    selected_post = BlogPost.query.get(index)
    return render_template("post.html", post=selected_post, year=current_year, month=current_month, date=current_date)


# New Post
@app.route("/make-post.html", methods=['GET', 'POST'])
def create_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=form.author.data,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template(url_for("create_new_post"), form=form)


# Edit Post
@app.route("/edit-post/<int:post_id>", methods=["GET", 'POST'])
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = edit_form.author.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("home", post_id=post.id))
    return render_template(url_for('create_new_post'), form=edit_form, is_edit=True)


# Delete Post
@app.route("/delete/<int:post_id>")
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


# About
@app.route('/about.html')
def about():
    return render_template(url_for('about'), year=current_year)


# Contact
@app.route('/contact.html', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        username = request.form['name']
        user_mail = request.form['email']
        user_phone = request.form['phone']
        user_message = request.form['message']
        send_message(username, user_mail, user_phone, user_message)
        return render_template(url_for('contact'), year=current_year, msg_sent=True)
    return render_template("url_for('contact')", year=current_year, msg_sent=False)


if __name__ == "__main__":
    app.run(debug=True)
