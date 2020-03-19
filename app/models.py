from datetime import datetime
from app import db, app, whooshee
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from hashlib import md5
from time import time
import jwt
from dataclasses import dataclass
from flask import current_app

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128))
	about_me = db.Column(db.String(140))
	last_seen = db.Column(db.DateTime, default=datetime.utcnow)
	posts = db.relationship('Post', backref='author', lazy='dynamic')
	units = db.relationship('Unit', backref='owner', lazy='dynamic')

	followed = db.relationship(
		'User', secondary=followers,
		primaryjoin=(followers.c.follower_id == id),
		secondaryjoin=(followers.c.followed_id == id),
		backref=db.backref('followers', lazy='dynamic'),
		lazy='dynamic'
	)

	role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
	role = db.relationship('Role', back_populates='users')

	def __init__(self):
		self.set_role()

	def follow(self, user):
		if not self.is_following(user):
			self.followed.append(user)

	def unfollow(self, user):
		if self.is_following(user):
			self.followed.remove(user)

	def is_following(self, user):
		return self.followed.filter(
			followers.c.followed_id == user.id).count() > 0

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

	def followed_posts(self):
		followed = Post.query.join(
			followers, (followers.c.followed_id == Post.user_id)).filter(
			followers.c.follower_id == self.id)
		own = Post.query.filter_by(user_id=self.id)
		return followed.union(own).order_by(Post.timestamp.desc())

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

@dataclass
@whooshee.register_model('name', 'comment')
class Unit(db.Model):
	id: int
	name: str
	age: int
	timestamp: datetime
	comment: str

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(40))
	age = db.Column(db.Integer)
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	comment = db.Column(db.String(140))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	def __repr__(self):
		return '<Item {}>'.format(self.comment)



class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	def __repr__(self):
		return '<Post {}>'.format(self.body)

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
