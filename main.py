from flask import Flask, Response, jsonify, request, render_template
# from flask import Flask, flash, request, redirect, Response , render_template
import json
import pyodbc
import urllib
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
#  from flask.ext.sqlalchemy import SQLAlchemy<--新版取消了
from flask_sqlalchemy import SQLAlchemy
import os

#  取得目前文件資料夾路徑
pjdir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
#  新版本的部份預設為none，會有異常，再設置True即可。
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
#  設置sqlite檔案路徑
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(pjdir, 'data.sqlite')


db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=False, nullable=False)

    def __init__(self, username, email):
        self.username = username
        self.email = email
    def __repr__(self):
        return '<User %r>' % self.username
    def to_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}


with app.app_context():
    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route('/users', methods=['GET'])
    def get_users():
        users = User.query.all()
        return jsonify([user.to_dict() for user in users])

    @app.route('/users/<int:user_id>', methods=['GET'])
    def get_user(user_id):
        user = User.query.get(user_id)
        if user is None:
            return jsonify({'error': 'User not found'}), 404
        return jsonify(user.to_dict())

    @app.route('/users', methods=['POST'])
    def create_user():
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        if not username or not email:
            return jsonify({'error': 'Username and email are required'}), 400
        user = User(username=username, email=email)
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': 'User created successfully', 'user_id': user.id}), 201

    @app.route('/users/<int:user_id>', methods=['PUT'])
    def update_user(user_id):
        user = User.query.get(user_id)
        if user is None:
            return jsonify({'error': 'User not found'}), 404
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        if not username or not email:
            return jsonify({'error': 'Username and email are required'}), 400
        user.username = username
        user.email = email
        db.session.commit()
        return jsonify({'message': 'User updated successfully', 'user_id': user.id})

    @app.route('/users/<int:user_id>', methods=['DELETE'])
    def delete_user(user_id):
        user = User.query.get(user_id)
        if user is None:
            return jsonify({'error': 'User not found'}), 404
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully', 'user_id': user_id})

    if __name__ == '__main__':
        db.create_all()
        app.run(debug=True)
