# -*- coding: utf-8 -*-
"""
summary_routes.py
Created on 18/02/2026
@author: Callum
"""
from flask import current_app, Blueprint, render_template

summary_bp = Blueprint('summary', __name__, url_prefix='/summary')

@summary_bp.route('/', methods=['GET'])
def get_summary_rt():
    summary = current_app.SummaryService.get_summary()
    return render_template('summary/summary_page.html', summary=summary)