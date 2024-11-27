from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.engine.cursor import CursorFetchStrategy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
import random

'''
Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)

# CREATE DB
class Base(DeclarativeBase):
    pass
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

    # below code is to convert database data to a dictionary
    # Because 'jsonify' can turn data to json if it is in dictionary form
    def to_dict(self):
        dictionary = {}
        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self,column.name)

        return dictionary




with app.app_context():
    db.create_all()




@app.route("/")
def home():
    return render_template("index.html")


@app.route("/random")
def rand():
    result = db.session.execute(db.select(Cafe))
    cafes = result.scalars().all()
    random_cafe = random.choice(cafes)
    return jsonify(cafe = random_cafe.to_dict())
    # Other way below
    # return jsonify(cafe={
    #     "id": random_cafe.id,
    #     "name": random_cafe.name,
    #     "map_url": random_cafe.map_url,
    #     "img_url": random_cafe.img_url,
    #     "location": random_cafe.location,
    #     "seats": random_cafe.seats,
    #     "has_toilet": random_cafe.has_toilet,
    #     "has_wifi": random_cafe.has_wifi,
    #     "has_sockets": random_cafe.has_sockets,
    #     "can_take_calls": random_cafe.can_take_calls,
    #     "coffee_price": random_cafe.coffee_price,
    # })

@app.route("/all")
def all_cafes():
    cafe_list = []
    cafes = db.session.execute(db.select(Cafe).order_by(Cafe.id)).scalars().all()
    for cafe in cafes:
        dict_ = cafe.to_dict()
        cafe_list.append(dict_)
    return jsonify(cafes = cafe_list)



@app.route("/search")
def get_cafe_at_location():
    query_location = request.args.get("loc")
    results = db.session.execute(db.select(Cafe).where(Cafe.location == query_location)).scalars().all()
    # Using list comprehension
    if results:
        return jsonify(cafes=[cafe.to_dict() for cafe in results])
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."}), 404

# Another way for above code
# @app.route("/search/loc=<loc>")
# def search(loc):
#     loc_list = []
#     locations = db.session.execute(db.select(Cafe).where(Cafe.location == loc)).scalars().all()
#     if locations:
#         for location in locations:
#             dict_ = location.to_dict()
#             loc_list.append(dict_)
#         return jsonify(cafes = loc_list)
#     else:
#         not_found = {
#             "Not Found":"Sorry, we dont have a cafe at that location"
#         }
#         return jsonify(error = not_found)

app.route('/add',methods=['POST'])
def add_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})



# HTTP GET - Read Record

# HTTP POST - Create Record

# HTTP PUT/PATCH - Update Record

# HTTP DELETE - Delete Record


if __name__ == '__main__':
    app.run(debug=True)
