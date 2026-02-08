# -*- coding: utf-8 -*-
"""
leaderboard_routes.py
Created on 06/02/2026
@author: Callum
"""
from flask import current_app, Blueprint, render_template, request, abort, jsonify, redirect, url_for
from Backend.Services.LeaderboardService import LeaderboardService

leaderboard_bp = Blueprint('leaderboard', __name__, url_prefix='/leaderboard')

@leaderboard_bp.route('/', methods=['GET'])
def get_leaderboard_rt():
    leaderboard = current_app.LeaderboardService.get_leaderboard()
    return render_template('leaderboard/leaderboard_page.html', leaderboard=leaderboard)