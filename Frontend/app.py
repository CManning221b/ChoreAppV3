# -*- coding: utf-8 -*-
"""
app.py
Created on 06/02/2026
@author: Callum
"""
from flask import Flask, render_template
from Frontend.config import config_by_name, file_names

from Backend.Managers.ChoreManager import ChoreManager
from Backend.Services.LeaderboardService import LeaderboardService
from Backend.Services.UserService import UserService
from Backend.Services.ChoreService import ChoreService


def create_app(config_name='development'):

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Set up services and managers
    app.choreManager = ChoreManager(file_names['UserFile'], file_names['ChoreFile'], file_names['InstanceFile'])
    app.choreManager.load_data()
    app.choreManager.reassign_all_chores()
    app.choreService = ChoreService(app.choreManager)
    app.userService = UserService(app.choreManager)
    app.LeaderboardService = LeaderboardService(app.choreManager)

    # Register blueprints
    from routes.main_routes import main_bp
    from routes.leaderboard_routes import leaderboard_bp
    from routes.auth_routes import auth_bp
    from routes.user_mng_routes import user_mng_bp
    from routes.user_chores import user_chores_bp
    from routes.chores_routes import chores_bp
    from routes.admin_routes import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(leaderboard_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_mng_bp)
    app.register_blueprint(user_chores_bp)
    app.register_blueprint(chores_bp)
    app.register_blueprint(admin_bp)

    # Setup error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='127.0.0.3', port=5000, debug=app.config['DEBUG'])
