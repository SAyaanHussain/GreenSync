from flask import Flask, render_template, request, redirect, url_for, flash, session
from pymongo import MongoClient
import certifi
import openai
from functools import wraps

app = Flask(__name__)
app.secret_key = 'hehe' 
client = MongoClient(
    "hehewon'ttellya",
    tls=True,
    tlsCAFile=certifi.where()
)

db = client['GreenSync']
users_collection = db['user_data']

@app.route('/error', methods=['GET'])
def err():
    return render_template('error.html')

@app.route('/sign-up', methods=['GET', 'POST'])
def sign():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if users_collection.find_one({'username': username}):
            flash('Username already exists. Try another one.')
            return redirect(url_for('sign'))
        users_collection.insert_one({'username': username, 'password': password})
        print("Account created")
        session['username'] = username

        return redirect(url_for('q1'))

    return render_template('sign-up.html')

@app.route('/', methods=['GET','POST'])
def login():
    if request.method=="POST":
        username = request.form['username']
        password = request.form['password']
        user = users_collection.find_one({'username': username})
        if user and user['password'] == password:
            session['username'] = username
            return redirect(url_for('home'))
        else:
            return redirect(url_for("err"))
    return render_template("login.html")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash("Please log in to access this page.")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/logout')
@login_required
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/login-survey-1', methods=['GET', 'POST'])
def q1():
    if request.method == 'POST':
        experience = request.form.get('experience')
        username = session.get('username')

        if experience is not None and username:
            users_collection.update_one(
                {'username': username},
                {'$set': {'experience': int(experience)}}
            )
            print(f"Saved experience {experience} for user {username}")
            return redirect(url_for('q2'))
        else:
            print("something error")
            return redirect(url_for('err'))

    return render_template("q1.html")



@app.route('/login-survey-2', methods=['GET', 'POST'])
def q2():
    if request.method == 'POST':
        challenges = request.form.getlist('challenge') 
        username = session.get('username')

        if challenges is not None and username:
            users_collection.update_one(
                {'username': username},
                {'$set': {'gardening_challenges': challenges}}
            )
            print(f"Saved challenges {challenges} for user {username}")
            return redirect(url_for('q3'))
        else:
            print("Something went wrong in q2 submission")
            return redirect(url_for('err'))

    return render_template('q2.html')


@app.route('/login-survey-3', methods=['GET','POST'])
def q3():
    if request.method=="POST":
        zones = request.form.getlist("zone")
        username = session.get("username")
        if zones is not None and username:
            users_collection.update_one(
                {'username':username},
                {'$set': {'zone': zones}}
            )
            print(f"Saved zone for user")
            return redirect(url_for('transition'))
    return render_template("q3.html")


@app.route('/onboarding-done')
def transition():
    return render_template("trans.html")

@app.route('/home')
@login_required
def home():
    username = session.get('username')
    user = users_collection.find_one({'username': username})
    return render_template("home.html", user=user)


if __name__ == '__main__':
    app.run(debug=True, port=7379)

if __name__ == '__main__':
    app.run(debug=True, port=7379)
