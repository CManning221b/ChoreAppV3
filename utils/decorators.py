# -*- coding: utf-8 -*-
"""
decorators.py
Created on 06/02/2026
@author: Callum
"""
from functools import wraps
from flask import session, redirect, url_for

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('is_admin') != True:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function