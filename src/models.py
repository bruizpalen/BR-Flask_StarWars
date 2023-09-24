from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    # people = db.relationship('People', secondary='favorite_people',
    #                          lazy='subquery', backref='user_id')
    # planets = db.relationship('Planets', secondary='favorite_planets',
    #                           lazy='subquery', backref='user_id')
    # vehicles = db.relationship('Vehicles', secondary='favorite_vehicles',
    #                            lazy='subquery', backref='user_id')

    def __repr__(self):
        return '<User %r>' % self.email

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "fav_people": [person.serialize() for person in self.fav_people],
            "fav_planets": [planet.serialize() for planet in self.fav_planets],
            # "vehicles": [vehicle.serialize() for vehicle in self.vehicles],
            # Do not serialize the password; it's a security breach
        }


class People(db.Model):
    __tablename__ = 'people'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    gender = db.Column(db.String(250), nullable=True)
    hair_color = db.Column(db.String(250), nullable=False)
    eye_color = db.Column(db.String(250), nullable=False)

    user_fav = db.relationship('User', secondary='favorite_people',
                           lazy='subquery', backref='fav_people')

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "gender": self.gender,
            "hair_color": self.hair_color,
            "eye_color": self.eye_color
        }


class Planets(db.Model):
    __tablename__ = 'planets'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    population = db.Column(db.Integer, nullable=False)
    terrain = db.Column(db.Integer, nullable=False)

    user_fav = db.relationship('User', secondary='favorite_planets',
                           lazy='subquery', backref='fav_planets')

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "population": self.population,
            "terrain": self.terrain,
        }


class Vehicles(db.Model):
    __tablename__ = 'vehicles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)

    user_fav = db.relationship('User', secondary='favorite_vehicles',
                           lazy='subquery', backref='fav_vehicles')

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "capacity": self.capacity
        }


class FavoritePeople(db.Model):
    __tablename__ = 'favorite_people'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    people_id = db.Column(db.Integer, db.ForeignKey('people.id'))


class FavoriteVehicles(db.Model):
    __tablename__ = 'favorite_vehicles'
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class FavoritePlanets(db.Model):
    __tablename__ = 'favorite_planets'
    id = db.Column(db.Integer, primary_key=True)
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
