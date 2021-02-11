# importing in core Flask modules
from flask import Flask, render_template, url_for, redirect, request, flash
from flask_sqlalchemy import SQLAlchemy
import json
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FileField
# this is for getting the secret key
with open('secrets.json') as f:
  data = json.load(f)

# Flask config stuff
app = Flask(__name__)
app.config['SECRET_KEY'] = data['secret_key']
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
password = data['password']

# Model for links for the database
class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(50), unique=True, nullable=False)
    dest = db.Column(db.String(150), nullable=False)

# Form for adding links to the database
class AddLink(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5, max=20)])
    url = StringField('Custom URL Ending', validators=[DataRequired(), Length(min=3, max=20)])
    dest = StringField('Destination URL', validators=[DataRequired(), Length(min=3, max=148)])
    submit = SubmitField('Submit')

    # def validate_url(self, url):
    #     link = Link.query.filter_by(url=url.data).first()
    #     if link:
    #         raise ValidationError('This link is already being used. Either choose a new one ')

# redirect to homepage
@app.route('/', methods=['GET', 'POST'])
def home():
    form = AddLink()
    if form.validate_on_submit():
        if form.password.data == password:
            link = Link.query.filter_by(url=form.url.data).first()
            if link:
                link.dest = form.dest.data
                db.session.commit()
            else:
                link = Link(url=form.url.data, dest=form.dest.data)
                db.session.add(link)
                db.session.commit()
            flash(f'Successfully Created Link: {form.url.data}')
        else:
            flash('Error Adding/Updating Link')
    return render_template('home.html', form=form)

@app.route('/view', methods=['GET'])
def view():
    links = Link.query.all()
    return render_template('links.html', links=links)

@app.route('/<id>', methods=['GET'])
def thing(id):
    link = Link.query.filter_by(url=id).first()
    if link:
        return redirect(link.dest)
    else:
        flash('Could not find link')
        return redirect(url_for('home'))

# this is what allows you to run the app
if __name__ == "__main__":
    app.run(debug=True)