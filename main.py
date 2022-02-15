from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random as rand


app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        dictionary = {}
        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self, column.name)
            # print(f"column:{column.name} dict:{dictionary}")
        return dictionary


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.route('/random')
def get_random_cafe():
    cafes = db.session.query(Cafe).all()
    random_cafe = rand.choice(cafes)
    # cafes_json_data = jsonify(
    #     cafes={
    #         "id": random_choice.id,
    #         "name": random_choice.name,
    #         "map_url": random_choice.map_url,
    #         "img_url": random_choice.img_url,
    #         "location": random_choice.location,
    #         "seats": random_choice.seats,
    #         "has_toilet": random_choice.has_toilet,
    #         "has_wifi": random_choice.has_wifi,
    #         "has_sockets": random_choice.has_sockets,
    #         "can_take_calls": random_choice.can_take_calls,
    #         "coffee_price": random_choice.coffee_price
    #     }
    # )
    # print(json.loads(cafes_json_data.get_data()))

    return jsonify(cafe=random_cafe.to_dict())


@app.route('/all')
def get_all_cafes():
    cafes = db.session.query(Cafe).all()
    cafes_list = [cafe.to_dict() for cafe in cafes]
    return jsonify(cafes=cafes_list)


@app.route('/search/')
def search_cafe():
    location = request.args
    word = location["loc"]
    cafe_query = Cafe.query.filter_by(location=word.title()).first()
    if cafe_query:
        return jsonify(cafe=cafe_query.to_dict())
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location"})
# HTTP POST - Create Record


@app.route('/add', methods=['GET', 'POST'])
def add_cafe():
    if request.method == "POST":
        new_cafe = Cafe(
            name=request.form['name'],
            map_url=request.form['map_url'],
            img_url=request.form["img_url"],
            location=request.form["location"],
            has_toilet=eval(request.form["has_toilet"]),
            seats=request.form["seats"],
            has_wifi=eval(request.form["has_wifi"]),
            has_sockets=eval(request.form["has_sockets"]),
            can_take_calls=eval(request.form["can_take_calls"]),
            coffee_price=request.form["coffee_price"]
        )
        db.session.add(new_cafe)
        db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe"})


# HTTP PUT/PATCH - Update Record
@app.route('/update-price/<cafe_id>', methods=['GET', 'PATCH'])
def update(cafe_id):
    try:
        update_data = request.args
        new_price = update_data['new_price']
        cafe_to_update = Cafe.query.get(cafe_id)
        cafe_to_update.coffee_price = new_price
        db.session.commit()
        return jsonify(success="Successfully Updated the Price")
    except AttributeError:
        return jsonify(error={"Not Found": "Sorry a Cafe with that id was not found in the database"}), 404


# HTTP DELETE - Delete Record
@app.route('/report-closed/<cafe_id>', methods=['GET', 'DELETE'])
def delete_record(cafe_id):
    try:
        api_key = request.args['api-key']
        if api_key == 'TopSecretKey':
            cafe_to_delete = Cafe.query.get(cafe_id)
            if cafe_to_delete:
                db.session.delete(cafe_to_delete)
                db.session.commit()
                return jsonify(success = "The Cafe data has successfully being deleted"),200
            else:
                return jsonify(Error = {"Not Found": "Sorry a Cafe With that id cannot be found in the database"}), 404
        else:
            return jsonify(Error="The API key inserted is incorrect"), 403
    except KeyError:
        return jsonify(error="Your API Key is required"), 403


if __name__ == '__main__':
    app.run(debug=True)
