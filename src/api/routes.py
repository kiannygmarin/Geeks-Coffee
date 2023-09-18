"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, jsonify, url_for, Blueprint,  current_app  
from api.models import db, User, Products
from api.utils import generate_sitemap, APIException

from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from werkzeug.security import generate_password_hash, check_password_hash
from base64 import b64encode
import os 
api = Blueprint('api', __name__)

def set_password(password, salt):
    return generate_password_hash(f"{password}{salt}")


def check_password(hash_password, password, salt):
    return check_password_hash(hash_password, f"{password}{salt}")

@api.route('/hello', methods=['POST', 'GET'])
def handle_hello():

    response_body = {
        "message": "Hello! I'm a message that came from the backend, check the network tab on the google inspector and you will see the GET request"
    }

    return jsonify(response_body), 200
@api.route('/signup', methods=["POST"])
def signup():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    address = request.json.get("address", None)
    name = request.json.get("name", None)
    username = request.json.get("username", None)
    age = request.json.get("age", None)
    city = request.json.get("city", None)
    phone = request.json.get("phone", None)

    salt = b64encode(os.urandom(32)).decode('utf-8')
    password = set_password(password, salt) 
    existing_email = User.query.filter_by(email=email).first()
    if existing_email:
        return jsonify({"msg": "email already exists"}), 400
    new_user = User(username=username, password=password, address=address,
                    name=name, age=age, city=city, phone=phone, email=email, salt=salt )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"user_id": new_user.id}), 200

## Muestra todos los productos
@api.route("/products", methods=["GET"])
def getProducts():
    products = Products.query.all()
    results = list(map(lambda x: x.serialize(), products ))
    print (results)
    return jsonify(results), 200

## Crea un producto
@api.route("/products", methods=["POST"])
def addProducts():
    body=json.loads(request.data)
    queryNewproducts=Products.query.filter_by(name=body["name"]).first()
    if queryNewproducts is None:
        new_products=Products(name=body["name"], 
        image=body["image"],
        description=body["description"],
        price=body["price"]
        )
        db.session.add(new_products)
        db.session.commit()
        response_body={
            "msg":"new product added"
        }
        return jsonify(new_products.serialize()), 200
    response_body={
            "msg":"product already created"
        }
    return jsonify(response_body), 400


@api.route("/login", methods=["POST"])
def login():
    if request.method == "POST":
        body = request.json
        email = body.get("email", None)
        password = body.get("password", None)

        if email is None or password is None :
            return jsonify("You need an email and a password"), 400
        else:
            user = User.query.filter_by(email=email).one_or_none()
            if user is None:
                return jsonify({"message": "Bad credentials"}), 400
            else:
                if check_password(user.password,password,user.salt):
                    token = create_access_token(identity=user.id)
                    return jsonify({"token": token}), 200
                else:
                    return jsonify({"message": "Bad credentials"}), 400
                
            #    if check_password(user.password, password, user.salt):
            #         token = create_access_token(identity=user.id)
            #         return jsonify({"token": token}), 200
            #     else:
            #         return jsonify({"message": "Bad credentials"}), 400
    
    access_token = create_access_token(identity =email)
    return jsonify(access_token= access_token)

