try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin

from flask import request, redirect, url_for, current_app, flash
from app.models import User, Role, Permission
from app import db
import os

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def redirect_back(default='/index', **kwargs):
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))

def init_role_permission():
    for user in User.query.all():
        if user.role is None:
            if user.email == current_app.config['ADMIN_EMAIL']:
                user.role = Role.query.filter_by(name='Administrator').first()
            else:
                user.role = Role.query.filter_by(name='User').first()
        db.session.add(user)
    db.session.commit()

def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ))

def delete_file(directory, filename):
    file = os.path.join(directory, filename)
    if os.path.exists(file):
        os.remove(file)
    else:
        print("no such file:", file)

def delete_avatar(filename):
    if filename:
        directory = current_app.config['AVATARS_SAVE_PATH']
        delete_file(directory, filename)


def addtodict3(thedict,key_a,key_b,key_c):
    if key_a in thedict:
        if key_b in thedict[key_a]:
            if key_c in thedict[key_a][key_b]:
                thedict[key_a][key_b][key_c] += 1
            else:
                thedict[key_a][key_b].update({key_c:1})
        else:
            thedict[key_a].update({key_b:{key_c:1}})
    else:
        thedict.update({key_a:{key_b:{key_c:1}}})
