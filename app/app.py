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
from sqlalchemy import func
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


def as_dic(table, exclude=None):
    data_list = []
    for u in table:
        data = u.__dict__
        data.pop('_sa_instance_state', None)
        if exclude is not None:
            for item in exclude:
                data.pop(item, None)
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
            data = jwt.decode(
                token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = T.Usuario.query.filter_by(
                public_id=data['public_id']).first()
        except:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kargs)

    return decorated


@app.route('/')
def index():
    return "APP POS"


@app.route('/categoria', methods=['GET', 'POST'])
def create_category():
    if request.method == 'POST':
        try:
            data = request.get_json()
            new_category = T.Categoria(
                codigo=data['codigo'], descricao=data['descricao'])
            db.session.add(new_category)
            db.session.commit()
            return jsonify({'message': 'Categoria adicionada com sucesso!'})
        except Exception as e:
            print('Error: %s' % e)
            return jsonify({'message': 'Error'})
    else:
        try:
            category = db.session.query(T.Categoria).all()
            return {"data": as_dic(category)}
        except Exception as e:
            print('Error: %s' % e)
            return jsonify({'message': 'Error'})


@app.route('/categoria/<codigo>', methods=['GET', 'PUT', 'DELETE'])
def get_one_category(codigo):
    #category = T.Categoria.query.filter((T.Categoria.codigo == codigo) | (func.lower(T.Categoria.descricao) == codigo.lower())).first()
    #category = db.session.query(T.Categoria).filter_by(codigo = codigo).first()
    category = db.session.query(T.Categoria).filter((T.Categoria.codigo == codigo) | (
        func.lower(T.Categoria.descricao) == codigo.lower())).first()

    if request.method == 'GET':
        try:
            if not category:
                return jsonify({'message': 'Categoria não encontrado'})

            data = {}
            data = category.__dict__
            data.pop('_sa_instance_state', None)
            return jsonify({"data": data})
        except Exception as e:
            print('Error: %s' % e)
            return jsonify({'message': 'Error'})
    elif request.method == 'PUT':
        try:
            if not category:
                return jsonify({'message': 'Categoria não encontrado'})

            data = request.get_json()
            category.descricao = data['descricao']
            db.session.flush()
            db.session.commit()
            return jsonify({"message": 'Categoria atualizada'})
        except Exception as e:
            print('Error: %s' % e)
            return jsonify({'message': 'Categoria não atualizada!'})
    elif request.method == 'DELETE':
        try:
            if not category:
                return jsonify({'message': 'Categoria não encontrado'})

            db.session.delete(category)
            db.session.flush()
            db.session.commit()
            return jsonify({"message": 'Categoria atualizada'})
        except Exception as e:
            print('Error: %s' % e)
            return jsonify({'message': 'Categoria não atualizada!'})


@app.route('/usuario', methods=['POST'])
@token_required
def create_user(current_user):
    if not current_user.admin:
        return jsonify({'message': 'Função não permitida para esse usuário!'})
    try:
        data = request.get_json()
        hashed_password = generate_password_hash(
            data['senha'], method='sha256')
        new_user = T.Usuario(public_id=str(
            uuid4()), nome=data['nome'], email=data['email'], senha=hashed_password, admin=data['admin'])
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "Novo usuário criado!"})
    except Exception as e:
        print(e)
        return jsonify({"error": "Error"})


@app.route('/usuario/<public_id>')
@token_required
def get_user(current_user, public_id):
    user = T.Usuario.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message': 'Usuário não encontrado!'})

    data = user.__dict__
    data.pop('_sa_instance_state', None)
    data.pop('senha')
    return jsonify({"data": data})


@app.route('/usuarios', methods=['GET'])
@token_required
def get_all_users(current_user):
    if not current_user.admin:
        return jsonify({'message': 'Função não permitida para esse usuário!'})

    users = db.session.query(T.Usuario).all()
    return {"data": as_dic(users, ['senha'])}


@app.route('/login')
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response("Could not verify", 401, {'WWW-Authenticate': 'Basic realm="Login required!'})

    user = T.Usuario.query.filter_by(nome=auth.username).first()

    if not user:
        return make_response('Not user found', 401, {'WWWW-Authenticate': 'Basic realm="Login required!'})

    if check_password_hash(user.senha, auth.password):
        token = jwt.encode({'public_id': user.public_id, 'exp': datetime.datetime.utcnow(
        ) + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'], algorithm="HS256")
        return jsonify({'token': token})

    return make_response('Not user found', 401, {'WWWW-Authenticate': 'Basic realm="Login required!'})


if __name__ == '__main__':
    app.run(debug=True, port=9999)
