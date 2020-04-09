from datetime import datetime
from app import db, app, whooshee
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from hashlib import md5
from time import time
import jwt
from flask import current_app, url_for

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128))
	about_me = db.Column(db.String(140))
	last_seen = db.Column(db.DateTime, default=datetime.utcnow)
	units = db.relationship('Unit', backref='owner', lazy='dynamic')
	records = db.relationship('Record', backref='author', lazy='dynamic')

	role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
	role = db.relationship('Role', back_populates='users')

	def __init__(self, username, email):
		self.set_role()
		self.username = username
		self.email = email

	def __repr__(self):
		return '<User {}>'.format(self.username)

	def can(self, permission_name):
		permission = Permission.query.filter_by(name=permission_name).first()
		return permission is not None and self.role is not None and \
			   permission in self.role.permissions

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

	def set_role(self):
		if self.role is None:
			if self.email == current_app.config['ADMIN_EMAIL']:
				self.role = Role.query.filter_by(name='Administrator').first()
			else:
				self.role = Role.query.filter_by(name='User').first()
			db.session.commit()

	def avatar(self, size):
		digest = md5(self.email.lower().encode('utf-8')).hexdigest()
		return 'https://www.gravatar.com/avatar/{}?d=robohash&s={}'.format(
			digest, size)

	def get_reset_password_token(self, expires_in=600):
		return jwt.encode(
			{'reset_password': self.id, 'exp': time() + expires_in},
			app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

	@staticmethod
	def verify_reset_password_token(token):
		try:
			id = jwt.decode(token, app.config['SECRET_KEY'],
							algorithms=['HS256'])['reset_password']
		except:
			return
		return User.query.get(id)


@whooshee.register_model('name')
class Unit(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(40))
	age = db.Column(db.Integer)
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	comment = db.Column(db.String(140))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	records = db.relationship('Record', backref='owner', lazy='dynamic')
	avatar_raw = db.Column(db.String(64))
	avatar_s= db.Column(db.String(64))
	avatar_m = db.Column(db.String(64))
	avatar_l = db.Column(db.String(64))

	def __repr__(self):
		return '<Item {}>'.format(self.comment)

	def avatar(self, size):
		if self.avatar_l != None:
			if size <= 30:
				filename = self.avatar_s
			elif size < 100:
				filename = self.avatar_m
			else:
				filename = self.avatar_l
			return url_for('get_avatar', filename=filename)
		digest = md5(self.name.lower().encode('utf-8')).hexdigest()
		return 'https://www.gravatar.com/avatar/{}?d=wavatar&s={}'.format(
			digest, size)


@whooshee.register_model('body')
class Record(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	complaint = db.Column(db.String(140))
	history = db.Column(db.String(140))
	results = db.Column(db.String(140))
	assessment = db.Column(db.String(140))
	plan = db.Column(db.String(140))
	prescriptions = db.Column(db.String(140))
	demographics = db.Column(db.String(140))
	body = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	def __repr__(self):
		return '<Record {} {}>'.format(self.body, self.id)


@login.user_loader
def load_user(id):
	return User.query.get(int(id))

roles_permissions = db.Table('roles_permissions',
                             db.Column('role_id', db.Integer, db.ForeignKey('role.id')),
                             db.Column('permission_id', db.Integer, db.ForeignKey('permission.id'))
                             )


class Role(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(30), unique=True)
	users = db.relationship('User', back_populates='role')
	permissions = db.relationship('Permission', secondary=roles_permissions, back_populates='roles')

	def __repr__(self):
		return 'Role {}'.format(self.name)

	@staticmethod
	def init_role():
		roles_permissions_map = {
			'Locked': ['POST', 'EDIT'],
			'User': ['POST', 'EDIT', 'DELETE'],
			'Administrator': ['POST', 'EDIT', 'DELETE', 'ADMINISTER']
		}
		for role_name in roles_permissions_map:
			role = Role.query.filter_by(name=role_name).first()
			if role is None:
				role = Role(name=role_name)
				db.session.add(role)
			role.permissions = []
			for permission_name in roles_permissions_map[role_name]:
				permission = Permission.query.filter_by(name=permission_name).first()
				if permission is None:
					permission = Permission(name=permission_name)
					db.session.add(permission)
				role.permissions.append(permission)
		db.session.commit()


class Permission(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(30), unique=True)
	roles = db.relationship('Role', secondary=roles_permissions, back_populates='permissions')

	def __repr__(self):
		return 'Permission {}'.format(self.name)
