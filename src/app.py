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
    # expected request_data form:
    #     {
    #     "email": "email",
    #     "password": "password"
    # }
    # The id is automatically added

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
def get_user_details_by_id(id):
    # Get the details of an user by the id
    try:
        user = User.query.get_or_404(id)
        serialized_user = user.serialize()
        for person in user.fav_people:
            print(person.id)
        return jsonify(serialized_user), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500


@app.route('/users', methods=['GET'])
def get_all_users():
    # Get all the users in the database
    try:
        users = User.query.all()
        serialized_users = [user.serialize() for user in users]
        return jsonify(serialized_users), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500


@app.route('/delete/<int:id>', methods=['DELETE'])
def delete_user_by_id(id):
    # Remove one user by id from the database
    try:
        user = User.query.get_or_404(id)
        db.session.delete(user)
        db.session.commit()
        return jsonify({"msg": "User successfully deleted"}), 200
    except Exception as e:
        return jsonify({"msg": f"Error: {str(e)}"}), 500


@app.route('/update/<int:id>', methods=['PATCH'])
def update_user_by_id(id):
    # Update the details concerning a certain user, given its id.
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
    # Get all people (characters) that is in the database
    people = People.query.all()
    people_serialized = [person.serialize() for person in people]
    return jsonify({"msg": "People succesfully accessed", "people": people_serialized}), 200


@app.route('/people/<int:people_id>', methods=['GET'])
def get_people_by_id(people_id):
    # Get the details of a certain character by the id
    try:
        people_selected = People.query.get_or_404(people_id)
        serialized_people = people_selected.serialize()
        return jsonify(serialized_people), 200
    except Exception as e:
        s
        return jsonify({"message": f"Error: {str(e)}"}), 500


@app.route('/create_people', methods=['POST'])
def create_people():
    # Create a new character
    request_data = request.get_json(force=True)
    # expected request_data form:
    #     {
    #     "name": "name",
    #     "gender": "female/male"
    #     "hair_color": "n/a",
    # }
    # The id is automatically added

    name = request_data.get("name", "n/a")

    # Check if a person with the same name already exists
    existing_person = People.query.filter_by(name=name).first()
    if existing_person:
        return jsonify({"message": "Person with this name already exists"}), 400

    gender = request_data.get("gender", "n/a")
    hair_color = request_data.get("hair_color", "n/a")
    eye_color = request_data.get("eye_color", "n/a")
    new_people = People(name=name, gender=gender,
                        hair_color=hair_color, eye_color=eye_color)

    try:
        db.session.add(new_people)
        db.session.commit()
        return jsonify({"message": "Person registered successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error: {str(e)}"}), 500


@app.route('/create_planet', methods=['POST'])
def create_planet():
    # Create planet with the request body as follows:
    # {
    #     "name": "planet2",
    #     "population": 20000,
    #     "terrain": 15

    # }
    request_data = request.get_json(force=True)

    name = request_data.get("name")
    population = request_data.get("population", "n/a")
    terrain = request_data.get("terrain", "n/a")

    # Check if a planet with the same name already exists
    existing_planet = Planets.query.filter_by(name=name).first()
    if existing_planet:
        return jsonify({"message": "Planet with this name already exists"}), 400

    new_planet = Planets(name=name, population=population, terrain=terrain)

    try:
        db.session.add(new_planet)
        db.session.commit()
        return jsonify({"message": "Planet registered successfully", "planet": new_planet.serialize()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error: {str(e)}"}), 500


@app.route('/planets', methods=['GET'])
def get_all_planets():
    try:
        planets = Planets.query.all()
        serialized_planets = [planet.serialize() for planet in planets]
        return jsonify(serialized_planets), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500


@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet_by_id(planet_id):
    try:
        planet_selected = Planets.query.get_or_404(planet_id)
        serialized_planet = planet_selected.serialize()
        return jsonify(serialized_planet), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500


@app.route('/user/<int:id>/favorites', methods=['POST'])
def add_fav_to_user(id):
    # When a user select a character or a planet as favorite by its name, the info will be send as follows
    # {
    #     "people": ["test_uncomplete"],
    #     "planets": ["planet2"]
    # }

    # also it can be changed to id instead of name and the code refactorized
    fav_dictionary = request.get_json(force=True)
    user_to_add_fav = User.query.get_or_404(id)

    try:
        if 'people' in fav_dictionary:
            people_names = fav_dictionary['people']
            people_ids = []
            for name in people_names:
                person = People.query.filter_by(name=name).first()
                if person:
                    people_ids.append(person)
            user_to_add_fav.fav_people.extend(people_ids)
            db.session.commit()
        if 'planets' in fav_dictionary:
            planets_names = fav_dictionary['planets']
            planets_ids = []
            for name in planets_names:
                planet = Planets.query.filter_by(name=name).first()
                if planet:
                    planets_ids.append(planet)
            user_to_add_fav.fav_planets.extend(planets_ids)
            db.session.commit()

        return jsonify({"message": 'Favorites have been updated', "fav_people": [person.serialize() for person in user_to_add_fav.fav_people], "fav_planets": [planet.serialize() for planet in user_to_add_fav.fav_planets]}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)} mal"}), 500


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
