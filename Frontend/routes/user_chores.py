# -*- coding: utf-8 -*-
"""
user_chores.py
Created on 06/02/2026
@author: Callum
"""
from flask import current_app, Blueprint, render_template, session, request, redirect, url_for
from Backend.Services.UserService import UserService
from utils.decorators import login_required


user_chores_bp = Blueprint('user_chores', __name__, url_prefix='/myChores')


@user_chores_bp.route('/', methods=['GET'])
@login_required
def get_my_chores():
    user_id = session.get('user_id')
    chores = current_app.userService.get_user_chores(user_id)
    return render_template('user/myChores.html', chores=chores)


@user_chores_bp.route('/complete/<instance_id>', methods=['POST'])
@login_required
def mark_chore_complete(instance_id):
    try:
        current_app.choreManager.complete_chore(instance_id)
        return redirect(url_for('user_chores.get_my_chores'))
    except Exception as e:
        return redirect(url_for('user_chores.get_my_chores'))