from flask_sqlalchemy import SQLAlchemy
from geopy.distance import geodesic
from geopy.distance import geodesic
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from flask import flash, redirect
from wtforms import StringField, PasswordField, SubmitField, SelectField
import sqlite3
import os
import requests
from sqlalchemy import func, desc, asc

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///offices.db'
app.config['SECRET_KEY'] = os.urandom(24)
db = SQLAlchemy(app)


DATABASE = 'users.db'

def create_table():
    with sqlite3.connect(DATABASE) as connection:
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                surname TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                country TEXT NOT NULL,
                city TEXT NOT NULL
            )
        ''')
        connection.commit()

create_table()
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    surname = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    country = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<User(name={self.name}, surname={self.surname}, email={self.email})>"
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Office(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    days_open = db.Column(db.String(255), nullable=False)
    opening_time = db.Column(db.String(255), nullable=False)
    closing_time = db.Column(db.String(255), nullable=False)
    telephone = db.Column(db.String(20), nullable=False)
 
    def __repr__(self):
        return f"<Office(name={self.name}, address={self.address}, latitude={self.latitude}, longitude={self.longitude})>"
class Vehicle(db.Model):
     id = db.Column(db.Integer, primary_key=True)
     name = db.Column(db.String(255), nullable=False)
     transmission = db.Column(db.String(50), nullable=False)
     fuelType = db.Column(db.String(50), nullable=False)
     deposit = db.Column(db.Float, nullable=False)
     mileage = db.Column(db.Float, nullable=False)
     age = db.Column(db.Integer, nullable=False)
     cost = db.Column(db.Float, nullable=False)
     picture = db.Column(db.String(255), nullable=True)
     office_id = db.Column(db.Integer, db.ForeignKey('office.id'), nullable=False)

     def __repr__(self):
        return f"<Vehicle(name={self.name}, transmission={self.transmission},fuelType={self.fuelType}, deposit={self.deposit}, mileage={self.mileage}, age={self.age}, cost={self.cost}), picture={self.picture}, office_id={self.office_id})>"

with app.app_context():
    db.create_all()

   
    fake_offices = [
        Office(name="AraçKirala Alsancak şube", address="Vasıf Çınar Blv 11-3 Kültür, 35220 Konak/İzmir", latitude=38.430787, longitude=27.138837, days_open="Pazartesi-Pazar", opening_time="09:00", closing_time="20:00", telephone="0532-754-32-11"),
        Office(name="AraçKirala Karşıyaka şube", address="2032. Sk. No:6 Atakent, 35590 Aosb/Karşıyaka", latitude=38.464571, longitude=27.088232, days_open="Pazartesi-Pazar", opening_time="08:00", closing_time="20:00", telephone="0532-754-32-12"),
        Office(name="AraçKirala Urla şube", address="2144. Sk. 2-20 Atatürk, 35430 Urla/İzmir", latitude=38.359471, longitude=26.777649, days_open="Pazartesi-Pazar", opening_time="08:00", closing_time="20:00", telephone="0532-754-32-13"),
        Office(name="AraçKirala Gaziemir şube", address="38/6. Sk. No:67 Egepark Evleri, 35410 Gaziemir", latitude=38.328986, longitude=27.119868, days_open="Pazartesi-Pazar", opening_time="08:00", closing_time="20:00", telephone="0532-754-32-14"),
        Office(name="AraçKirala Fatih şube", address="Zeyrek 34083 Fatih/İstanbul", latitude=41.018380, longitude=28.953773, days_open="Pazartesi-Pazar", opening_time="08:00", closing_time="20:00", telephone="0532-754-32-15"),
        Office(name="AraçKirala Beşiktaş şube", address="Sinanpaşa, Beşiktaş/İstanbul", latitude=41.044477, longitude=29.006219, days_open="Pazartesi-Pazar", opening_time="08:00", closing_time="20:00", telephone="0532-754-32-16"),
        Office(name="AraçKirala Ataşehir şube", address="Küçükbakkalköy Ataşehir/İstanbul", latitude=40.985121, longitude=29.123995, days_open="Pazartesi-Pazar", opening_time="08:00", closing_time="20:00", telephone="0532-754-32-17"),
        Office(name="AraçKirala Beykoz şube", address="Tokatköy 34825 Beykoz/İstanbul", latitude=41.157432, longitude=29.094933, days_open="Pazartesi-Pazar", opening_time="08:00", closing_time="20:00", telephone="0532-754-32-18"),
    ]   
    
    fake_vehicles = [
        Vehicle(name="Citroen C1", transmission="Otomatik", fuelType="Benzin",deposit=500.0, mileage=20000.0, age=2, cost=800.0, picture="images/citroenC1.webp",office_id=1),
        Vehicle(name="Citroen C", transmission="Manuel", fuelType="Dizel",deposit=1000.0, mileage=22000.0, age=5, cost=1000.0, picture="images/CitroenCpng.png", office_id=1),
        Vehicle(name="Fiat Egea", transmission="Manuel", fuelType="Benzin",deposit=500.0, mileage=25000.0, age=3, cost=1500.0, picture="images/FiatEgea.webp", office_id=1),
        Vehicle(name="Kia Stonic", transmission="Otomatik", fuelType="Dizel",deposit=300.0, mileage=10000.0, age=4, cost=500.0, picture="images/kiaStonic.png", office_id=1),
        Vehicle(name="Mercedez-Benz Vito", transmission="Otomatik", fuelType="Benzin",deposit=1000.0, mileage=20000.0, age=4, cost=3000.0, picture="images/Mercedes-BenzVito.webp", office_id=2),
        Vehicle(name="Nissan Qahqai", transmission="Manuel", fuelType="Dizel",deposit=1000.0, mileage=28000.0, age=3, cost=1200.0, picture="images/NissanQashqai.webp", office_id=2),
        Vehicle(name="Opel Corsa", transmission="Manuel", fuelType="Benzin",deposit=500.0, mileage=25000.0, age=3, cost=1500.0, picture="images/OpelCorsa.png", office_id=2),
        Vehicle(name="Opel Mokka", transmission="Otomatik", fuelType="Dizel",deposit=2300.0, mileage=10000.0, age=1, cost=2500.0, picture="images/OpelMokka.png", office_id=2),
        Vehicle(name="Peugeot 508", transmission="Otomatik", fuelType="Benzin",deposit=1000.0, mileage=15000.0, age=2, cost=2000.0, picture="images/Peugeot508.webp", office_id=3),
        Vehicle(name="Peugeot 2008", transmission="Otomatik", fuelType="Dizel",deposit=2000.0, mileage=12000.0, age=1, cost=3000.0, picture="images/Peugeot2008.png", office_id=3),
        Vehicle(name="Renault Clio", transmission="Manuel", fuelType="Benzin",deposit=500.0, mileage=24000.0, age=3, cost=1000.0, picture="images/RenaultClio.webp", office_id=3),
        Vehicle(name="Renault Symbol", transmission="Otomatik", fuelType="Dizel",deposit=800.0, mileage=10000.0, age=1, cost=1100.0, picture="images/RenaultSymbol.png", office_id=4),
        Vehicle(name="Citroen C1", transmission="Otomatik", fuelType="Benzin",deposit=300.0, mileage=180000.0, age=4, cost=700.0, picture="images/citroenC1.webp", office_id=4),
        Vehicle(name="Citroen C", transmission="Manuel", fuelType="Benzin",deposit=1000.0, mileage=25000.0, age=3, cost=1000.0, picture="images/CitroenCpng.png", office_id=4),
        Vehicle(name="Fiat Egea", transmission="Manuel", fuelType="Dizel",deposit=700.0, mileage=28000.0, age=3, cost=1000.0, picture="images/FiatEgea.webp", office_id=5),
        Vehicle(name="Suziki Vitera", transmission="Otomatik", fuelType="Dizel",deposit=900.0, mileage=30000.0, age=2, cost=1300.0, picture="images/SuzikiVitera.webp", office_id=5),
        Vehicle(name="Opel Corsa", transmission="Otomatik", fuelType="Benzin",deposit=800.0, mileage=25000.0, age=2, cost=1500.0, picture="images/OpelCorsa.png", office_id=5),
        Vehicle(name="Opel Mokka", transmission="Manuel", fuelType="Dizel",deposit=2300.0, mileage=10000.0, age=2, cost=2800.0, picture="images/OpelMokka.png", office_id=6),
        Vehicle(name="Peugeot 508", transmission="Manuel", fuelType="Dizel",deposit=1000.0, mileage=15000.0, age=3, cost=2000.0, picture="images/Peugeot508.webp", office_id=6),
        Vehicle(name="Peugeot 2008", transmission="Otomatik", fuelType="Benzin",deposit=2000.0, mileage=12000.0, age=1, cost=3000.0, picture="images/Peugeot2008.png", office_id=7),
        Vehicle(name="Mercedez-Benz Vito", transmission="Otomatik", fuelType="Dizel",deposit=2000.0, mileage=20000.0, age=4, cost=4000.0, picture="images/Mercedes-BenzVito.webp", office_id=7),
        Vehicle(name="Nissan Qahqai", transmission="Otomatik", fuelType="Benzin",deposit=1000.0, mileage=28000.0, age=3, cost=1200.0, picture="images/NissanQashqai.webp", office_id=8),
         Vehicle(name="Fiat Egea", transmission="Otomatik", fuelType="Dizel",deposit=600.0, mileage=23000.0, age=3, cost=1000.0, picture="images/FiatEgea.webp", office_id=8),
        Vehicle(name="Suziki Vitera", transmission="Manuel", fuelType="Benzin",deposit=700.0, mileage=11000.0, age=2, cost=1300.0, picture="images/SuzikiVitera.webp", office_id=8),
    ]

    existing_offices = Office.query.all()
    existing_vehicles = Vehicle.query.all()

    if not existing_offices:
        for fake_office in fake_offices:
            db.session.add(fake_office)

    if not existing_vehicles:
        for fake_vehicle in fake_vehicles:
            db.session.add(fake_vehicle)

    db.session.commit()



class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    country = SelectField('Country', choices=[('türkiye', 'Türkiye')], validators=[DataRequired()])
    city = SelectField('City', choices=[('izmir', 'İzmir'), ('istanbul', 'İstanbul')], validators=[DataRequired()])
    submit = SubmitField('Üye Ol')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Giriş Yap')

@app.route('/')
def homepage():
    user_name = session.get('user_name')
    userCity = session.get('userCity')
    is_logged_in = True if user_name else False
    return render_template('homepage.html', user_name=user_name, is_logged_in=is_logged_in,userCity=userCity)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = User(
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data,
            country=form.country.data,
            city=form.city.data
        )
        new_user.set_password(form.password.data)

        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            flash('Login successful!', 'success')
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['userCity'] = user.city
            return redirect(url_for('homepage'))
        else:
            flash('Invalid email or password', 'danger')

    return render_template('login.html', form=form)

@app.route('/get_office_names')
def get_office_names():
    office_names = [office.name for office in Office.query.all()]
    return jsonify(office_names)




@app.route('/search_result')
def search_result():
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    office_name = request.args.get('office')
    days_difference = int(request.args.get('days',default=1))
    print("Days difference is:", days_difference)

  
    selected_office = Office.query.filter_by(name=office_name).first()
    vehicles_query = Vehicle.query.filter_by(office_id=selected_office.id)

   
    brand_filter = request.args.get('brand')
    transmission_filter = request.args.get('transmission')
    price_order = request.args.get('order')

    if brand_filter:
        vehicles_query = vehicles_query.filter(Vehicle.name.like(f'%{brand_filter}%'))

    if transmission_filter:
        vehicles_query = vehicles_query.filter_by(transmission=transmission_filter)

   
    if price_order == 'asc':
        vehicles_query = vehicles_query.order_by(asc(Vehicle.cost))
    elif price_order == 'desc':
        vehicles_query = vehicles_query.order_by(desc(Vehicle.cost))

    vehicles = vehicles_query.all()

    unique_brands = db.session.query(func.distinct(Vehicle.name)).all()
    unique_brands = [brand[0] for brand in unique_brands]
    default_price_order = 'random'


  
    return render_template('search_result.html', start_date=start_date, end_date=end_date, office_name=office_name,
                           days_difference=days_difference, vehicles=vehicles, unique_brands=unique_brands,
                           default_price_order=default_price_order)

@app.route('/get_office_locations')
def get_office_locations():
    userCity = session.get('userCity')

    if userCity:
      
        if userCity.lower() == 'izmir':
            offices = Office.query.limit(4).all()
        elif userCity.lower() == 'istanbul':
            offices = Office.query.offset(4).limit(4).all()
    else:
       
        user_location = get_user_location()  
        if user_location:
            offices = get_nearby_offices(user_location)
        else:
            offices = []

    office_data = [
        {'name': office.name,'address':office.address ,'days_open':office.days_open,'opening_time':office.opening_time ,'closing_time':office.closing_time ,'telephone':office.telephone ,'latitude': office.latitude, 'longitude': office.longitude}
        for office in offices
    ]
    return jsonify(office_data)
    import requests

def get_user_location():
    try:
        
        response = requests.get('https://ipinfo.io')
        data = response.json()

      
        location = data.get('loc', '').split(',')
        if len(location) == 2:
            latitude, longitude = map(float, location)
            return {'latitude': latitude, 'longitude': longitude}
        else:
            return None
    except Exception as e:
        print(f'Error getting user location: {e}')
        return None


def get_nearby_offices(user_location):
   
    nearby_offices = [
        office for office in Office.query.all()
        if calculate_distance(user_location, {'latitude': office.latitude, 'longitude': office.longitude}) <= 30
    ]
    return nearby_offices

def calculate_distance(location1, location2):
    return geodesic((location1['latitude'], location1['longitude']),
                    (location2['latitude'], location2['longitude'])).kilometers



if __name__ == '__main__':
    app.run(debug=True)
