# -*- coding: utf-8 -*-
"""
auth_routes.py
Created on 06/02/2026
@author: Callum
"""
from flask import current_app, Blueprint, render_template, session, request, redirect, url_for
from Backend.Services.UserService import UserService

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('auth/login.html')

    # POST - handle form submission
    email = request.form.get('email')
    password = request.form.get('password')

    user = current_app.userService.authenticate(email, password)

    if user:
        session['user_id'] = user.id
        session['user_name'] = user.name
        session['is_admin'] = user.properties.get('is_admin', False)
        return redirect(url_for('main.index'))

    return render_template('auth/login.html', error='Invalid credentials')

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('auth.login'))


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('auth/signup.html')

    # POST - handle form submission
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')

    exclude_keys = {'name', 'email', 'password'}
    properties = {key: value for key, value in request.form.items() if key not in exclude_keys}

    for key in properties:
        properties[key] = properties[key] == 'on' if isinstance(properties[key], str) else properties[key]

    properties['is_admin'] = False

    try:
        user = current_app.userService.create_user(
            name=name,
            email=email,
            password=password,
            properties=properties
        )
        return redirect(url_for('auth.login'))
    except ValueError as e:
        return render_template('auth/signup.html', error=str(e))