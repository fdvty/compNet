#coding=utf-8
from flask import render_template, flash, redirect, url_for, request, send_from_directory
from app import app, avatars, db
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Unit, Record, Evaluation
from app.email import send_password_reset_email
from app.utils import redirect_back, flash_errors, delete_avatar, addtodict3
from app.forms import LoginForm, UnitForm, RegistrationForm, EditProfileForm, RecordForm, \
    ResetPasswordForm, ResetPasswordRequestForm, UploadAvatarForm, CropAvatarForm, AddRecordForm, \
    EvaluateForm
from datetime import datetime
from werkzeug.urls import url_parse
import app.evaluator as evaluator
from sqlalchemy import func

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('home.html')


@app.route('/dashboards', methods=['GET', 'POST'])
@login_required
def dashboards():
    # 下面这一行完成的是分类统计，按照Evaluation.gender，统计两个性别的人数
    # evaluations = db.session.query(Evaluation.gender, func.sum(1)).group_by(Evaluation.gender).all()
    # for row in evaluations:
    #     print(row[0], row[1])
    #     if row[0] == 0:
    #         gender_data.append(['Male', row[1]/total])
    #     else:
    #         gender_data.append(['Female', row[1]/total])

    suspected_male = 0
    suspected_female = 0
    data_0 = [0, 0, 0, 0, 0]
    data_1 = [0, 0, 0, 0, 0]
    data_susp = []
    data_safe = []
    for evaluation in db.session.query(Evaluation).filter(Evaluation.result >= 0.8).all():
        index = int(evaluation.age / 20)
        if(index > 4):
            index = 4
        if evaluation.gender == 0:
            data_0[index] += 1
            suspected_male += 1
        else:
            data_1[index] += 1
            suspected_female += 1
        data_susp.append([evaluation.rbc, evaluation.wbc])

    for evaluation in db.session.query(Evaluation).filter(Evaluation.result < 0.8).all():
        data_safe.append([evaluation.rbc, evaluation.wbc])

    # 获取Evaluation的总数
    total = Evaluation.query.count()
    gender_data = []
    gender_data.append(['Male', suspected_male / total])
    gender_data.append(['Female', suspected_female / total])


    #----------------------- 在这里填写data_map，格式为data_sample的格式 -----------------------------

    data_map = {}
    for evaluation in Evaluation.query.all():
        if(evaluation.result >= 0.8):
            addtodict3(data_map, evaluation.continent, evaluation.country, "Suspected")
        else:
            addtodict3(data_map, evaluation.continent, evaluation.country, "Normal")

    print(data_map)

    # data_sample = {
    #     "Asia": {
    #         "Sri Lanka": {
    #             "Suspected": "75",
    #             "Normal": "2"
    #         },
    #         "Bangladesh": {
    #             "Suspected": "7",
    #             "Normal": "20"
    #         }
    #     },
    #     "Europe": {
    #         "Poland": {
    #             "Suspected": "1",
    #             "Normal": "0"
    #         },
    #         "Norway": {
    #             "Suspected": "1",
    #             "Normal": "0"
    #         },
    #     }
    # }
    #
    # data_map = data_sample

    #---------------------------------------------------------------------

    # 下面这一行中的 xxx=xxx 语句是把 xxx 传递到html，这样在html里就可以用 " {{ xxx }} " 的方式引用传过去的变量了
    return render_template('dashboards.html', gender_data=gender_data, data_0=data_0, data_1=data_1, data_susp=data_susp, data_safe=data_safe, data_map=data_map)

@app.route('/patient_profile/<int:unit_id>', methods=['GET', 'POST'])
@login_required
def patient_profile(unit_id):
    unit = Unit.query.get(unit_id)
    form = RecordForm()
    if form.validate_on_submit():
        record = Record(complaint=form.complaint.data, history=form.history.data, results=form.results.data, assessment=form.assessment.data,
                        plan=form.plan.data, prescriptions=form.prescriptions.data, demographics=form.demographics.data, body=form.body.data,
                        owner=unit, author=current_user)
        db.session.add(record)
        db.session.commit()
        flash('Your record is now live!', category='info')
        return redirect(url_for('patient_profile', unit_id=unit.id))
    page = request.args.get('page', 1, type=int)
    pagination = unit.records.order_by(Record.timestamp.desc()).paginate(page, app.config['UNITS_PER_PAGE'], False)
    records = pagination.items
    if unit.owner == current_user or current_user.can('ADMINISTER') == True:
        return render_template('patient_profile.html', page=page, pagination=pagination, records=records, form=form, unit=unit)
    else:
        return render_template('patient_profile.html', page=page, pagination=pagination, records=records, unit=unit)


@app.route('/record/manage')
@login_required
def record_manage():
    q = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    if q == '':
        pagination = Record.query.order_by(Record.timestamp.desc()).paginate(page, app.config['RECORDS_PER_PAGE'], False)
    else:
        pagination = Record.query.whooshee_search(q).order_by(Record.timestamp.desc()).paginate(page, app.config['RECORDS_PER_PAGE'], False)
    records = pagination.items
    # return jsonify(units)
    return render_template('manage_record.html', page=page, pagination=pagination, records=records)


@app.route('/record/add', methods=['GET', 'POST'])
@login_required
def record_add():
    form = AddRecordForm()
    form.unit_id.choices = [(u.id, u.name) for u in Unit.query.order_by(Unit.timestamp.desc()).all()]
    if form.validate_on_submit():
        record = Record(complaint=form.complaint.data, history=form.history.data, results=form.results.data, assessment=form.assessment.data,
                        plan=form.plan.data, prescriptions=form.prescriptions.data, demographics=form.demographics.data, body=form.body.data,
                        owner=Unit.query.get(form.unit_id.data), author=current_user)
        db.session.add(record)
        db.session.commit()
        flash('Your record is now live!', category='info')
        return redirect_back()
    page = request.args.get('page', 1, type=int)
    pagination = Record.query.order_by(Record.timestamp.desc()).paginate(
        page, app.config['RECORDS_PER_PAGE_ADD'], False)
    records = pagination.items
    return render_template('add_record.html', title='Add Record', form=form,
                           records=records, pagination=pagination)


@app.route('/record/<int:record_id>/delete', methods=['POST'])
@login_required
def record_delete(record_id):
    record = Record.query.get(record_id)
    if(current_user != record.author and current_user.can('ADMINISTER') == False):
        flash('Permission Denied.', 'warning')
        return redirect_back()
    db.session.delete(record)
    db.session.commit()
    flash('Record deleted.', 'success')
    return redirect_back()

@app.route('/record/<int:record_id>/edit', methods=['GET', 'POST'])
@login_required
def record_edit(record_id):
    record = Record.query.get(record_id)
    if(current_user != record.author and current_user.can('ADMINISTER') == False):
        flash('Permission Denied.', 'warning')
        return redirect_back()
    form = RecordForm()
    if form.validate_on_submit():
        record.complaint = form.complaint.data
        record.history = form.history.data
        record.results = form.results.data
        record.assessment = form.assessment.data
        record.plan = form.plan.data
        record.prescriptions = form.prescriptions.data
        record.demographics = form.demographics.data
        record.body = form.body.data
        record.timestamp = datetime.utcnow()
        db.session.commit()
        flash('Your changes have been saved.', category='info')
        return redirect_back()
    elif request.method == 'GET':  # 这里要区分第一次请求表格的情况
        form.complaint.data = record.complaint
        form.history.data = record.history
        form.results.data = record.results
        form.assessment.data = record.assessment
        form.plan.data = record.plan
        form.prescriptions.data = record.prescriptions
        form.demographics.data = record.demographics
        form.body.data = record.body
    return render_template('edit_record.html', title='Edit Record', record=record, form=form)  # 和POST表格后出错的情况



@app.route('/unit/add', methods=['GET', 'POST'])
@login_required
def unit_add():
    form = UnitForm();
    if form.validate_on_submit():
        unit = Unit(name=form.name.data, comment=form.comment.data, gender=form.gender.data, height=form.height.data,
                    weight=form.weight.data, age=form.age.data, owner=current_user)
        db.session.add(unit)
        db.session.commit()
        flash('Your unit is now live!', category='info')
        return redirect_back()
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
    return render_template('manage_unit.html', page=page, pagination=pagination, units=units)

@app.route('/unit/<int:unit_id>/delete', methods=['POST'])
@login_required
def unit_delete(unit_id):
    unit = Unit.query.get(unit_id)
    if(current_user != unit.owner and current_user.can('ADMINISTER') == False):
        flash('Permission Denied.', 'warning')
        return redirect_back()
    for record in Record.query.filter_by(owner=unit).all():
        db.session.delete(record)
    db.session.delete(unit)
    db.session.commit()
    flash('Unit deleted.', 'success')
    return redirect_back()

@app.route('/unit/<int:unit_id>/edit', methods=['GET', 'POST'])
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
        unit.gender = form.gender.data
        unit.height = form.height.data
        unit.weight = form.weight.data
        db.session.commit()
        flash('Your changes have been saved.', category='info')
        return redirect_back()
    elif request.method == 'GET':  # 这里要区分第一次请求表格的情况
        form.name.data = unit.name
        form.age.data = unit.age
        form.comment.data = unit.comment
        form.gender.data = unit.gender
        form.height.data = unit.height
        form.weight.data = unit.weight
    return render_template('edit_unit.html', title='Edit Unit', unit=unit, form=form)  # 和POST表格后出错的情况



@app.route('/unit/<int:unit_id>/settings/avatar')
@login_required
def change_avatar(unit_id):
    unit = Unit.query.get(unit_id)
    if (current_user != unit.owner and current_user.can('ADMINISTER') == False):
        flash('Permission Denied.', 'warning')
        return redirect_back()
    upload_form = UploadAvatarForm()
    crop_form = CropAvatarForm()
    return render_template('change_avatar.html', upload_form=upload_form, crop_form=crop_form, unit=unit)


@app.route('/unit/<int:unit_id>/settings/avatar/upload', methods=['POST'])
@login_required
def upload_avatar(unit_id):
    unit = Unit.query.get(unit_id)
    form = UploadAvatarForm()
    if form.validate_on_submit():
        image = form.image.data
        filename = avatars.save_avatar(image)
        delete_avatar(unit.avatar_raw)
        unit.avatar_raw = filename
        db.session.commit()
        flash('Image uploaded, please crop.', 'success')
    flash_errors(form)
    return redirect(url_for('change_avatar', unit_id=unit.id))


@app.route('/unit/<int:unit_id>/settings/avatar/crop', methods=['POST'])
@login_required
def crop_avatar(unit_id):
    unit = Unit.query.get(unit_id)
    form = CropAvatarForm()
    if form.validate_on_submit():
        x = form.x.data
        y = form.y.data
        w = form.w.data
        h = form.h.data
        filenames = avatars.crop_avatar(unit.avatar_raw, x, y, w, h)
        delete_avatar(unit.avatar_s)
        delete_avatar(unit.avatar_m)
        delete_avatar(unit.avatar_l)
        unit.avatar_s = filenames[0]
        unit.avatar_m = filenames[1]
        unit.avatar_l = filenames[2]
        db.session.commit()
        flash('Avatar updated.', 'success')
        return redirect(url_for('patient_profile', unit_id=unit.id))
    flash_errors(form)
    return redirect(url_for('change_avatar', unit_id=unit.id))


@app.route('/avatars/<path:filename>')
def get_avatar(filename):
    return send_from_directory(app.config['AVATARS_SAVE_PATH'], filename)

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
    return render_template('user.html', user=user)


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
        return redirect_back()
    elif request.method == 'GET':  # 这里要区分第一次请求表格的情况
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)  # 和POST表格后出错的情况


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

@app.route('/quick_evaluation', methods=['GET', 'POST'])
@login_required
def quick_evaluation():
    page = request.args.get('page', 1, type=int)
    pagination = Evaluation.query.order_by(Evaluation.timestamp.desc()).paginate(
        page, app.config['EVALUATIONS_PER_PAGE_ADD'], False)
    evaluations = pagination.items
    return render_template('quick_evaluation.html', title='Quick Evaluate', evaluations=evaluations, pagination=pagination, page=page)

@app.route('/add_evaluation', methods=['GET', 'POST'])
@login_required
def add_evaluation():
    form = EvaluateForm()
    if form.validate_on_submit():
        # load model
        model = evaluator.load_model()
        field_names = ['gender', 'age', 'contact_history', 'acid_test', 'x_ray', 'wbc', 'rbc', 'hgb', 'continent', 'country']
        datas = {field_name: getattr(form, field_name).data for field_name in field_names}
        result = round(evaluator.estimate(model, datas), 5)
        evaluation = Evaluation(**datas, result=result)
        db.session.add(evaluation)
        db.session.commit()
        flash('Your evaluation is now live!', category='success')
        return redirect_back()
    return render_template('add_evaluation.html', title='Add Evaluate', form=form)

@app.route('/delete_evaluation/<int:evaluation_id>', methods=['POST'])
@login_required
def delete_evaluation(evaluation_id):
    evaluation = Evaluation.query.get(evaluation_id)
    if(current_user.can('ADMINISTER') == False):
        flash('Permission Denied.', 'warning')
        return redirect_back()
    db.session.delete(evaluation)
    db.session.commit()
    flash('Evaluation deleted.', 'success')
    return redirect_back()
