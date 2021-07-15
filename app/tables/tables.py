from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.types import Float, String, Boolean
from sqlalchemy.sql.sqltypes import Integer

from app import db


class Usuario(db.Model):
    __tablename__ = 'usuario'
    __table_args__ = {"schema": "pos"}

    id = db.Column(Integer, primary_key=True)
    public_id = db.Column(String(50), unique=True)
    nome = db.Column(String(100))
    email = db.Column(String(300), unique=True)
    senha = db.Column(String)
    admin = db.Column(Boolean)


class Unidade(db.Model):
    __tablename__ = 'unidade_medida'
    __table_args__ = {"schema": "pos"}

    id = db.Column(Integer, primary_key=True)
    codigo = db.Column(String, nullable=False)
    descricao = db.Column(String, nullable=False)


class Embalagem(db.Model):
    __tablename__ = 'embalagem'
    __table_args__ = {"schema": "pos"}

    id = db.Column(Integer, primary_key=True)
    codigo = db.Column(String, nullable=False)
    descricao = db.Column(String, nullable=False)


class Categoria(db.Model):
    __tablename__ = 'categoria'
    __table_args__ = {"schema": "pos"}

    id = db.Column(Integer, primary_key=True)
    codigo = db.Column(String, nullable=False, unique=True)
    descricao = db.Column(String, nullable=False)


class SubCategoria(db.Model):
    __tablename__ = 'sub_categoria'
    __table_args__ = {"schema": "pos"}

    id = db.Column(Integer, primary_key=True)
    codigo = db.Column(String, nullable=False)
    descricao = db.Column(String, nullable=False)
    categoria = db.Column(Integer, nullable=False)


class Produto(db.Model):
    __tablename__ = 'produto'
    __table_args__ = {"schema": "pos"}

    id = db.Column(Integer, primary_key=True)
    codigo = db.Column(String(30), unique=True)
    nome = db.Column(String(100), nullable=False)
    descricao = db.Column(String)
    preco = db.Column(Float)
    validade = db.Column(Integer)
    unidade = db.Column(Integer)
    embalagem = db.Column(Integer)
    categoria = db.Column(Integer)


def create_table():
    db.drop_all()
    db.create_all()
