# -*- coding: utf-8 -*-
"""
chores_routes.py
Created on 07/02/2026
@author: Callum
"""
from flask import current_app, Blueprint, render_template
from Backend.Services.ChoreService import ChoreService

chores_bp = Blueprint('chores', __name__, url_prefix='/chores')

@chores_bp.route('/', methods=['GET'])
def get_chores_rt():
    chores_data = current_app.choreService.get_all_chores_instances()
    return render_template('chores/chores_page.html', chores_data=chores_data)

@chores_bp.route('/history', methods=['GET'])
def get_chores_history_rt():
    history_data = current_app.choreService.get_chore_history(limit=100)
    return render_template('chores/chores_history_page.html', history_data=history_data)