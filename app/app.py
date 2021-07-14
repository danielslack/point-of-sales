"""
file name: app.py 
Date: 12/07/2021
Author: Daniel Caria
email: daniel@dmltech.com.br

"""

# Libs
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
from functools import wraps


load_dotenv()


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET')

db = SQLAlchemy(app)

# as_dic return list of dictionary of tables from database
# Params: table = table name, exclude = field exclude of return
def as_dic(table, exclude):
    data_list = [] 
    for u in table:
        data = u.__dict__
        data.pop('_sa_instance_state', None)
        for item in exclude:
            data.pop(item,None)
        data_list.append(data)
    return data_list


# token_required valid user and password
def token_required(f):
    @wraps(f)
    def decorated(*args, **kargs):
        token = None
        
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
            
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
           data = jwt.decode(token, app.config['SECRET_KEY'],algorithms=["HS256"])
           current_user = T.Usuario.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message':'Token is invalid!'}) , 401
        
        return f(current_user, *args, **kargs)
    
    return decorated


@app.route('/')
@token_required
def index(current_user):
    
    if not current_user.admin:
        return jsonify('Permissão não permitida para esse usuário!')
    
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
        return jsonify({"message": "Novo usuário criado!"})
    except Exception as e:
        print(e)
        return jsonify({"error": "Error"})
    
@app.route('/usuario/<public_id>')
def get_user(public_id):
    user = T.Usuario.query.filter_by(public_id=public_id).first()
    
    if not user:
        return jsonify({'message': 'Usuário não encontrado!'})

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
        token = jwt.encode({'public_id': user.public_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'], algorithm="HS256")
        return jsonify({'token': token})
    
    return make_response('Not user found', 401, {'WWWW-Authenticate': 'Basic realm="Login required!'})
 
 
 
if __name__ == '__main__':
    app.run(debug=True, port=9999)