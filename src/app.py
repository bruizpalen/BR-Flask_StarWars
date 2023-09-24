"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planets, Vehicles, FavoritePeople, FavoritePlanets, FavoriteVehicles
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/create_user', methods=['POST'])
def create_user():
    request_data = request.get_json(force=True)

    email = request_data.get("email")
    password = request_data.get("password")
    new_user = User(email=email, password=password, is_active=True)
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error: {str(e)}"}), 500


@app.route('/user/<int:id>', methods=['GET'])
def get_user_details(id):
    try:
        user = User.query.get_or_404(id)
        serialized_user = user.serialize()
        return jsonify(serialized_user), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500


@app.route('/users', methods=['GET'])
def get_all_users():
    try:
        users = User.query.all()
        serialized_users = [user.serialize() for user in users]
        return jsonify(serialized_users), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500


@app.route('/delete/<int:id>', methods=['DELETE'])
def delete_user_by_id(id):
    try:
        user = User.query.get_or_404(id)
        db.session.delete(user)
        db.session.commit()
        return jsonify({"msg": "User successfully deleted"}), 200
    except Exception as e:
        return jsonify({"msg": f"Error: {str(e)}"}), 500


@app.route('/update/<int:id>', methods=['PATCH'])
def update_user_by_id(id):
    user_data_to_update = request.get_json(force=True)
    try:
        user = User.query.get_or_404(id)
        new_email = user_data_to_update.get("email", user.email)
        new_password = user_data_to_update.get("password", user.password)
        user.email = new_email
        user.password = new_password
        db.session.commit()
        return jsonify({"msg": "User successfully updated"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"Error: {str(e)}"}), 500


@app.route('/people', methods=['GET'])
def get_all_people():
    people = People.query.all()
    people_serialized = [person.serialize() for person in people]
    return jsonify({"msg": "People succesfully accessed", "people": people_serialized}), 200


@app.route('/people/<int:people_id>', methods=['GET'])
def get_people_by_id(people_id):
    try:
        people_selected = People.query.get_or_404(people_id)
        serialized_people = people_selected.serialize()
        return jsonify(serialized_people), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500


@app.route('/create_people', methods=['POST'])
def create_people():
    request_data = request.get_json(force=True)

    name = request_data.get("name", "n/a")
    gender = request_data.get("gender", "n/a")
    hair_color = request_data.get("hair_color", "n/a")
    eye_color = request_data.get("eye_color", "n/a")
    new_people = People(name=name, gender=gender,
                        hair_color=hair_color, eye_color=eye_color)

    try:
        db.session.add(new_people)
        db.session.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error: {str(e)}"}), 500


@app.route('/planets', methods=['GET'])
def get_all_planets():
    planets = Planets.query.all()
    planets_serialized = [planet.serialize() for planet in planets]
    return jsonify({"msg": "Planets succesfully accessed", "planets": planets_serialized}), 200


@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet_by_id(planet_id):
    try:
        planet_selected = Planets.query.get_or_404(planet_id)
        serialized_planet = planet_selected.serialize()
        return jsonify(serialized_planet), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500


@app.route('/create_planet', methods=['POST'])
def create_planet():
    request_data = request.get_json(force=True)

    name = request_data.get("name", "n/a")
    population = request_data.get("population", "n/a")
    terrain = request_data.get("terrain", "n/a")
    new_planet = Planets(name=name, population=population,
                         terrain=terrain)
    try:
        db.session.add(new_planet)
        db.session.commit()
        return jsonify({"message": "Planet registered successfully", "planet": new_planet.serialize()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error: {str(e)}"}), 500


@app.route('/user/<int:id>/favorites', methods=['POST'])
def add_fav_to_user(id):
    fav_dictionary = request.get_json(force=True)
    user_to_add_fav = User.query.get_or_404(id)
    try:
        if fav_dictionary['people']:  # if 'people' if fav_dictionary
            people_names = fav_dictionary['people']
            people_ids = []
            for name in people_names:
                person = People.query.filter_by(name=name).first()
                if person:
                    people_ids.append(person.id)
            user_to_add_fav.people.extend(people_ids)
            db.session.commit()
        if fav_dictionary['planets']:  # if 'people' if fav_dictionary
            planets_names = fav_dictionary['planets']
            planets_ids = []
            for name in planets_names:
                planet = Planets.query.filter_by(name=name).first()
                if planet:
                    planets_ids.append(person.id)
            user_to_add_fav.planets.extend(planets_ids)
            db.session.commit()

        return jsonify({"message": 'Favorites have been updated', "people": user_to_add_fav.people, "planets": user_to_add_fav.planets}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500


@app.route('/delete/people/<int:id>', methods=['DELETE'])
def delete_people_by_id(id):
    try:
        person = People.query.get_or_404(id)
        db.session.delete(person)
        db.session.commit()
        return jsonify({"msg": "Person successfully deleted"}), 200
    except Exception as e:
        return jsonify({"msg": f"Error: {str(e)}"}), 500


@app.route('/delete/planet/<int:id>', methods=['DELETE'])
def delete_planet_by_id(id):
    try:
        planet = Planets.query.get_or_404(id)
        db.session.delete(planet)
        db.session.commit()
        return jsonify({"msg": "Planet successfully deleted"}), 200
    except Exception as e:
        return jsonify({"msg": f"Error: {str(e)}"}), 500


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
