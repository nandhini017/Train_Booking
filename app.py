from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------------- DATABASE MODELS ---------------- #

class Train(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    from_city = db.Column(db.String(100))
    to_city = db.Column(db.String(100))
    price = db.Column(db.Integer)
    image = db.Column(db.String(200))

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    train_id = db.Column(db.Integer)
    passenger_name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    seat_number = db.Column(db.String(10))
    pnr = db.Column(db.String(20))

# ---------------- ROUTES ---------------- #

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/trains', methods=['POST'])
def trains():
    from_city = request.form['from']
    to_city = request.form['to']
    trains = Train.query.filter_by(from_city=from_city, to_city=to_city).all()
    return render_template('trains.html', trains=trains)

@app.route('/seats/<int:train_id>')
def seats(train_id):
    return render_template('seats.html', train_id=train_id)

@app.route('/passenger/<int:train_id>/<seat>')
def passenger(train_id, seat):
    return render_template('passenger.html', train_id=train_id, seat=seat)

@app.route('/payment/<int:train_id>/<seat>', methods=['POST'])
def payment(train_id, seat):
    name = request.form['name']
    age = request.form['age']
    pnr = "FR" + str(random.randint(100000,999999))

    booking = Booking(
        train_id=train_id,
        passenger_name=name,
        age=age,
        seat_number=seat,
        pnr=pnr
    )

    db.session.add(booking)
    db.session.commit()

    return redirect(url_for('confirmation', pnr=pnr))

@app.route('/confirmation/<pnr>')
def confirmation(pnr):
    return render_template('confirmation.html', pnr=pnr)

# ---------------- INITIAL DATA ---------------- #

@app.before_first_request
def create_tables():
    db.create_all()
    if not Train.query.first():
        t1 = Train(name="Rajdhani Express", from_city="Delhi",
                   to_city="Mumbai", price=1200, image="train1.jpg")
        t2 = Train(name="Shatabdi Express", from_city="Chennai",
                   to_city="Bangalore", price=900, image="train2.jpg")
        db.session.add_all([t1, t2])
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)