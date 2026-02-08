# -*- coding: utf-8 -*-
"""
main_routes.py
Created on 04/02/2026
@author: Callum
"""
from datetime import datetime
from flask import Blueprint, render_template, current_app

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    leaderboard = current_app.LeaderboardService.get_leaderboard()
    chores_data = current_app.choreService.get_all_chores_instances()

    today = datetime.now().date()
    days_in_month = (datetime(today.year, today.month % 12 + 1, 1) - datetime(today.year, today.month, 1)).days
    days_left = days_in_month - today.day

    return render_template('main/index.html',
                           chores_data=chores_data,
                           leaderboard=leaderboard,
                           today=today,
                           days_left=days_left)
@main_bp.route('/about')
def about():
    return render_template('main/about.html')