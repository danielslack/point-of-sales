import os
import uuid
import jwt
import datetime
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.types import String
from sqlalchemy.sql.sqltypes import Integer
from tables import tables as T
from werkzeug.security import generate_password_hash, check_password_hash
from uuid import uuid4
from dotenv import load_dotenv

load_dotenv()


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET')

db = SQLAlchemy(app)

def as_dic(table, exclude):
    data_list = [] 
    for u in table:
        data = u.__dict__
        data.pop('_sa_instance_state', None)
        for item in exclude:
            data.pop(item,None)
        data_list.append(data)
    return data_list

@app.route('/')
def index():
    users = db.session.query(T.Usuario).all()
    return {"data": as_dic(users, ['senha'])}

@app.route('/usuario', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        hashed_password = generate_password_hash(data['senha'], method='sha256')
        new_user = T.Usuario(public_id = str(uuid4()) , nome=data['nome'], email=data['email'], senha=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "New user created!"})
    except Exception as e:
        print(e)
        return jsonify({"error": "Error"})
    
@app.route('/usuario/<public_id>')
def get_user(public_id):
    user = T.Usuario.query.filter_by(public_id=public_id).first()
    
    if not user:
        return jsonify({'message': 'No user found!'})

    data = user.__dict__
    data.pop('_sa_instance_state', None)
    data.pop('senha')
    return jsonify({"data": data})


@app.route('/login')
def login():
    auth = request.authorization
    
    if not auth or not auth.username or not auth.password:
        return make_response("Could not verify", 401, {'WWW-Authenticate': 'Basic realm="Login required!'})
    
    user = T.Usuario.query.filter_by(nome=auth.username).first()
    
    if not user:
        return make_response('Not user found', 401, {'WWWW-Authenticate': 'Basic realm="Login required!'})
    
    
    if check_password_hash(user.senha, auth.password):
        token = jwt.encode({'public_id': user.public_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('UTF-8')})
    
    return make_response('Not user found', 401, {'WWWW-Authenticate': 'Basic realm="Login required!'})
 
 
 
if __name__ == '__main__':
    app.run(debug=True, port=9999)