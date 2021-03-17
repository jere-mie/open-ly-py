# importing in core Flask modules
from flask import Flask, render_template, url_for, redirect, request, flash
from flask_sqlalchemy import SQLAlchemy
import json
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FileField
from flask_login import LoginManager, login_user, current_user, logout_user, login_required, UserMixin
import re
import os

# this is for getting the secret key
with open('secrets.json') as f:
  data = json.load(f)

# Flask config stuff
app = Flask(__name__)
app.config['SECRET_KEY'] = data['secret_key']
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

# Model for links for the database
class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(50), unique=True, nullable=False)
    dest = db.Column(db.String(150), nullable=False)

if not os.path.exists('site.db'):
    db.create_all()

# setting up login stuff
login_manager = LoginManager(app)
login_manager.login_view='login'
login_manager.login_message_category='info'

class User(UserMixin):
    pass

@login_manager.user_loader
def user_loader(username):
  user = User()
  user.id = username
  return user

# password for logging in
password = data['password']
domain = data['domain']

# Form for adding links to the database
class AddLink(FlaskForm):
    url = StringField('Custom URL Ending', validators=[DataRequired(), Length(min=3, max=20)])
    dest = StringField('Destination URL', validators=[DataRequired(), Length(min=3, max=148)])
    submit = SubmitField('Submit')

# Login Form
class LoginForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=2, max=20)])
    submit = SubmitField('Submit')


# redirect to homepage
@app.route('/', methods=['GET', 'POST'])
def home():
    form = AddLink()
    if current_user.is_authenticated:
        if form.validate_on_submit():
            # getting rid of bad chars
            form.url.data = form.url.data.strip()
            form.url.data = form.url.data.replace(' ', '-')
            form.url.data = re.sub(r'[^a-zA-Z0-9-]', '-', form.url.data)

            link = Link.query.filter_by(url=form.url.data).first()
            if link:
                link.dest = form.dest.data
                db.session.commit()
            else:
                link = Link(url=form.url.data, dest=form.dest.data)
                db.session.add(link)
                db.session.commit()
            flash(f'Successfully Created Link: \nhttp://{domain}/{form.url.data}', 'success')
    return render_template('home.html', form=form, data=data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        if form.password.data == password:
            user = User()
            user.id = "Jeff"
            login_user(user, remember=True)
            flash('login worked', 'success')
            return redirect(url_for('home'))
        else:
            flash('incorrect password!', 'danger')
    return render_template('login.html', form=form, data=data)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/view', methods=['GET'])
def view():
    if current_user.is_authenticated:
        links = Link.query.all()
        return render_template('links.html', links=links, data=data)
    flash('you must be logged in', 'danger')
    return redirect(url_for('home'))
@app.route('/delete/<id>', methods=['GET'])
def delete(id):
    if not current_user.is_authenticated:
        return redirect(url_for('home'))
    try:
        link = Link.query.filter_by(url=id).first()
    except:
        flash('error querying link', 'danger')
        return redirect(url_for('home'))
    if link:
        db.session.delete(link)
        db.session.commit()
        flash(f'successfully deleted link {domain}/{link.url}', 'success')
    else:
        flash('error deleting link')
    return redirect(url_for('home'))

@app.route('/<id>', methods=['GET'])
def thing(id):
    link = Link.query.filter_by(url=id).first()
    if link:
        return redirect(link.dest)
    else:
        flash('Could not find link', 'danger')
        return redirect(url_for('home'))

# this is what allows you to run the app
if __name__ == "__main__":
    app.run(debug=True)