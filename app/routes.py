from flask import render_template, flash, redirect, url_for, jsonify
from app import app
from app.forms import LoginForm, PostForm, UnitForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post, Unit
from werkzeug.urls import url_parse
from flask import request
from app.forms import RegistrationForm, EditProfileForm
from app import db
from datetime import datetime
from app.forms import ResetPasswordRequestForm
from app.email import send_password_reset_email
from app.forms import ResetPasswordForm
from app.utils import redirect_back

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
	form = PostForm()
	if form.validate_on_submit():
		post = Post(body=form.post.data, author=current_user)
		db.session.add(post)
		db.session.commit()
		flash('Your post is now live!', category='info')
		return redirect(url_for('index'))

	page = request.args.get('page', 1, type=int)
	posts = current_user.followed_posts().paginate(
		page, app.config['POSTS_PER_PAGE'], False)
	next_url = url_for('index', page=posts.next_num) \
		if posts.has_next else None
	prev_url = url_for('index', page=posts.prev_num) \
		if posts.has_prev else None
	return render_template('index.html', title='Home', form=form,
						   posts=posts.items, next_url=next_url,
                               prev_url=prev_url)

@app.route('/unit/add', methods=['GET', 'POST'])
@login_required
def unit_add():
    form = UnitForm();
    if form.validate_on_submit():
        unit = Unit(name=form.name.data, comment=form.comment.data,
                    age=form.age.data, owner=current_user)
        db.session.add(unit)
        db.session.commit()
        flash('Your unit is now live!', category='info')
        return redirect(url_for('unit_add'))
    page = request.args.get('page', 1, type=int)
    pagination = Unit.query.order_by(Unit.timestamp.desc()).paginate(
        page, app.config['UNITS_PER_PAGE_ADD'], False)
    units = pagination.items
    return render_template('add_unit.html', title='Add Unit', form=form,
                           units=units, pagination=pagination)


@app.route('/unit/manage')
@login_required
def unit_manage():
    q = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    if q == '':
        pagination = Unit.query.order_by(Unit.timestamp.desc()).paginate(page, app.config['UNITS_PER_PAGE'], False)
    else:
        pagination = Unit.query.whooshee_search(q).order_by(Unit.timestamp.desc()).paginate(page, app.config['UNITS_PER_PAGE'], False)
    units = pagination.items
    # return jsonify(units)
    return render_template('manage_unit.html', page=page, pagination=pagination, units=units, junits=jsonify(units))

@app.route('/unit/delete/<int:unit_id>', methods=['POST'])
@login_required
def unit_delete(unit_id):
    unit = Unit.query.get(unit_id)
    if(current_user != unit.owner and current_user.can('ADMINISTER') == False):
        flash('Permission Denied.', 'warning')
        return redirect_back()
    db.session.delete(unit)
    db.session.commit()
    flash('Unit deleted.', 'success')
    return redirect_back()

@app.route('/unit/edit/<int:unit_id>', methods=['GET', 'POST'])
@login_required
def unit_edit(unit_id):
    unit = Unit.query.get(unit_id)
    if(current_user != unit.owner and current_user.can('ADMINISTER') == False):
        flash('Permission Denied.', 'warning')
        return redirect_back()
    form = UnitForm()
    if form.validate_on_submit():
        unit.name = form.name.data
        unit.age = form.age.data
        unit.comment = form.comment.data
        unit.timestamp = datetime.utcnow()
        db.session.commit()
        flash('Your changes have been saved.', category='info')
        return redirect_back()
    elif request.method == 'GET':  # 这里要区分第一次请求表格的情况
        form.name.data = unit.name
        form.age.data = unit.age
        form.comment.data = unit.comment
    return render_template('edit_unit.html', title='Edit Unit', form=form)  # 和POST表格后出错的情况




@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', category='warning')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!', category='info')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.', category='info')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':  # 这里要区分第一次请求表格的情况
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)  # 和POST表格后出错的情况


@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username), category='warning')
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!', category='warning')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username), category='info')
    return redirect(url_for('user', username=username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username), category='warning')
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!', category='warning')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username), category='info')
    return redirect(url_for('user', username=username))


@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template("index.html", title='Explore', posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
            flash('Check your email for the instructions to reset your password', category='info')
        else:
            flash('This mail has not been registered', category='warning')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.', category='info')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)