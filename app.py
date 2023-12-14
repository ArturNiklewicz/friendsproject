from flask import Flask, render_template, request, redirect, session, flash
from _collections_abc import MutableMapping
from flask_ckeditor import CKEditor
from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, SubmitField, TextAreaField, IntegerField, HiddenField, DateField
from wtforms.validators import DataRequired, InputRequired, Length
import pyrebase

# Constants
LOGIN_URL = '/login'
REGISTER_URL = '/register'
ADMIN_URL = '/admin'

menu = [['LOGIN', LOGIN_URL], ['REGISTER', REGISTER_URL], ['ADMIN', ADMIN_URL]]

app = Flask(__name__)
app.config['SECRET_KEY'] = 'leyni'
app.config['SESSION_TYPE'] = 'filesystem'
ckeditor = CKEditor(app)

class Frm(FlaskForm):
    email = EmailField("Póstur:", validators=[InputRequired()])
    texti = TextAreaField("Texti:", validators=[InputRequired(),Length(min=5,max=15)])  # Birtum CKEditorinn í þessum í index.html
    takki = SubmitField("Takki")

menu = [['LOGIN','/login'], ['REGISTER', '/register'], ['ADMIN', '/admin']]
# Secret Key verður að vera set
# Settu þína config tenginu hér -> Project setting á FB.
config = {
    "apiKey": "AIzaSyAO83dR0bwlYM2o3c-qrGLpc4rUc7yIFnw",
    "databaseURL": "https://verkefni4-20cc5-default-rtdb.firebaseio.com/",
    "authDomain": "szczupak-verkefni.firebaseapp.com",
    "projectId": "szczupak-verkefni",
    "storageBucket": "szczupak-verkefni.appspot.com",
    "messagingSenderId": "986637855632",
    "appId": "1:986637855632:web:7cf80a5358f3ff8e6d2115",
    "measurementId": "G-GYS00R4W9L"
} 

fb = pyrebase.initialize_app(config)
auth = fb.auth()
db = fb.database()  #realtime database

@app.route('/delete_movie/<string:movie_id>', methods=['GET'])
def delete_movie(movie_id):
    db.child("MovieQuote").child(movie_id).remove()
    flash('Movie deleted successfully!', 'success')
    return redirect(url_for('/'))

@app.route('/')
def index():
    u = db.child("MovieQuote").get().val()
    lst = list(u.items())
    return render_template("index.html", menu=menu, lst=lst, f=Frm())

@app.route('/add_movie', methods=['GET', 'POST'])
def add_movie():
    if request.method == 'POST':
        title = request.form.get('title')
        quote = request.form.get('quote')
        director = request.form.get('director')

        if title and quote and director:
            # Add the new movie to the Firebase Realtime Database
            db.child("MovieQuote").push({"Name": title, "Quote": quote, "Director": director})
            flash('Movie added successfully!', 'success')
            return redirect(url_for('/'))

    return render_template('index.html', menu=menu)

@app.route('/todatabase')
def todb():
    # skrifum nýjan í grunn hnútur sem heitir notandi 
    db.child("MovieQuote").push({"Name":"The Hunger games","Quote":"Hope. It is the only thing stronger than fear.", "Director":"Francis Lawrence, Gary Ross"}) 
    return "Skrifum tilvitun í realtime database.."

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('pwd')
        try:
            user = auth.create_user_with_email_and_password(email, password)
            flash('Nýskráning tókst!', 'success')
            return redirect(url_for('/login'))
        except:
            flash('Nýskráning tókst ekki...', 'danger')
    return render_template('register.html', menu=menu)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form('email')
        password = request.form('pwd')
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            session['logger'] = True
            session['user_info'] = auth.get_account_info(user['idToken'])
            flash('Successful login', 'success')
            return redirect(url_for('/'))
        except Exception as e:
            flash('Incorrect username/password', 'danger')
    return render_template('login.html', menu=menu)

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('logger', None)
    flash('Þú hefur útskráð þig', 'info')
    return redirect(url_for('/'))

@app.route('/admin')
def admin():
    if 'logger' in session:
        user_info = session['user_info']
        return render_template('admin.html', currentUser=user_info)
    else:
        flash('Þú verður að skrá þig inn', 'warning')
        return redirect(url_for('/login'))
    
@app.route('/info', methods=["GET","POST"])
def info():

    if request.form:
        
        infoA = request.form.get('ckA')
        infoB = request.form.get('ckB')

        return render_template("info.html", infoA = infoA, infoB = infoB)
    else:
        return "má ekki..."
    
@app.route('/form_action', methods=["GET","POST"])
def action():
    #
    # Kóði hér til að taka úr forminu og gera eitthvað við gögnin
    #
    return "Þetta route gerir ekkert nema að grípa actionið úr forminu"

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html")

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
