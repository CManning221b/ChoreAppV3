# -*- coding: utf-8 -*-
"""
user_mng_routes.py
Created on 06/02/2026
@author: Callum
"""
from flask import current_app, Blueprint, render_template, session, request, redirect, url_for
from Backend.Services.UserService import UserService
from utils.decorators import login_required


user_mng_bp = Blueprint('user_mng', __name__, url_prefix='/profile')


@user_mng_bp.route('/', methods=['GET'])
@login_required
def profile():
    user_id = session.get('user_id')
    user = current_app.userService.get_user(user_id)
    return render_template('user/profile.html', user=user)


@user_mng_bp.route('/', methods=['POST'])
@login_required
def update_profile():
    user_id = session.get('user_id')
    user = current_app.userService.get_user(user_id)

    # Update basic info
    user.name = request.form.get('name', user.name)
    user.email = request.form.get('email', user.email)

    # Update properties (same logic as signup)
    exclude_keys = {'name', 'email'}
    properties = {key: value for key, value in request.form.items() if key not in exclude_keys}

    for key in properties:
        properties[key] = properties[key] == 'on' if isinstance(properties[key], str) else properties[key]

    # Merge new properties with existing (don't overwrite is_admin)
    user.properties.update(properties)

    current_app.choreManager.save_data()

    return redirect(url_for('user_mng.profile'))