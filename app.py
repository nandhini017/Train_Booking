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
    departure = db.Column(db.String(20))
    arrival = db.Column(db.String(20))
    price_sleeper = db.Column(db.Integer)
    price_3ac = db.Column(db.Integer)
    price_2ac = db.Column(db.Integer)
    price_1ac = db.Column(db.Integer)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    train_id = db.Column(db.Integer)
    passenger_name = db.Column(db.String(100))
    user_email = db.Column(db.String(100))
    user_phone = db.Column(db.String(20))
    age = db.Column(db.Integer)
    seat_number = db.Column(db.String(10))
    class_type = db.Column(db.String(10))
    travel_date = db.Column(db.String(20))
    price = db.Column(db.Integer)
    pnr = db.Column(db.String(20))

# ---------------- ROUTES ---------------- #

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/trains', methods=['POST'])
def trains():
    from_city = request.form['from']
    to_city = request.form['to']
    class_type = request.form.get('class_type', 'Sleeper')  # get selected class
    trains = Train.query.filter_by(from_city=from_city, to_city=to_city).all()
    return render_template('trains.html', trains=trains, class_type=class_type)

@app.route('/seats/<int:train_id>')
def seats(train_id):
    booked = Booking.query.filter_by(train_id=train_id).all()
    booked_seats = [b.seat_number for b in booked]
    return render_template('seats.html', train_id=train_id, booked_seats=booked_seats)

@app.route('/passenger/<int:train_id>/<seat>')
def passenger(train_id, seat):
    train = Train.query.get(train_id)
    return render_template('passenger.html', train=train, seat=seat)

@app.route('/payment/<int:train_id>/<seat>', methods=['POST'])
def payment(train_id, seat):
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    age = request.form['age']
    class_type = request.form['class_type']
    travel_date = request.form['travel_date']

    train = Train.query.get(train_id)

    # get price based on class
    if class_type == 'Sleeper':
        selected_price = train.price_sleeper
    elif class_type == '3AC':
        selected_price = train.price_3ac
    elif class_type == '2AC':
        selected_price = train.price_2ac
    elif class_type == '1AC':
        selected_price = train.price_1ac
    else:
        selected_price = train.price_sleeper

    pnr = "RB" + str(random.randint(100000, 999999))

    booking = Booking(
        train_id=train_id,
        passenger_name=name,
        user_email=email,
        user_phone=phone,
        age=age,
        seat_number=seat,
        class_type=class_type,
        travel_date=travel_date,
        price=selected_price,
        pnr=pnr
    )

    db.session.add(booking)
    db.session.commit()

    return redirect(url_for('confirmation', pnr=pnr))

@app.route('/confirmation/<pnr>')
def confirmation(pnr):
    booking = Booking.query.filter_by(pnr=pnr).first()
    train = Train.query.get(booking.train_id)
    return render_template('confirmation.html', booking=booking, train=train)

# ---------------- AUTO TRAIN DATA GENERATION ---------------- #

with app.app_context():
    db.create_all()

    if not Train.query.first():
        cities = [
            "Delhi", "Mumbai", "Chennai", "Bangalore", "Hyderabad",
            "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Lucknow",
            "Goa", "Coimbatore", "Patna", "Bhopal", "Indore",
            "Surat", "Nagpur", "Varanasi", "Vijayawada", "Mysore",
            "Thiruvananthapuram", "Madurai", "Ranchi", "Chandigarh",
            "Amritsar", "Guwahati", "Raipur", "Visakhapatnam",
            "Kanpur", "Udaipur"
        ]

        train_list = []

        for i in range(len(cities)):
            for j in range(len(cities)):
                if cities[i] != cities[j]:
                    train = Train(
                        name=f"{cities[i]}-{cities[j]} Express",
                        from_city=cities[i],
                        to_city=cities[j],
                        departure=f"{random.randint(1,12)}:{random.choice(['00','30'])} {'AM' if random.randint(0,1)==0 else 'PM'}",
                        arrival=f"{random.randint(1,12)}:{random.choice(['00','30'])} {'AM' if random.randint(0,1)==0 else 'PM'}",
                        price_sleeper=random.randint(500, 1500),
                        price_3ac=random.randint(1500, 2500),
                        price_2ac=random.randint(2000, 3000),
                        price_1ac=random.randint(2500, 4000)
                    )
                    train_list.append(train)

        db.session.add_all(train_list)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)