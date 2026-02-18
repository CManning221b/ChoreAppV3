# -*- coding: utf-8 -*-
"""
app.py
Created on 06/02/2026
@author: Callum
"""
from flask import Flask, render_template
from flask_mail import Mail
from apscheduler.schedulers.background import BackgroundScheduler

from Frontend.config import config_by_name, file_names


from Backend.Managers.ChoreManager import ChoreManager
from Backend.Services.LeaderboardService import LeaderboardService
from Backend.Services.UserService import UserService
from Backend.Services.ChoreService import ChoreService
from Backend.Services.SummaryService import SummaryService
from Backend.Services.EmailService import EmailService

mail = Mail()

def create_app(config_name='development'):

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Initialise mail
    mail.init_app(app)

    # Set up services and managers
    app.choreManager = ChoreManager(file_names['UserFile'], file_names['ChoreFile'], file_names['InstanceFile'], file_names['HistoryFile'], file_names['RecentlyAssigned'])
    app.choreManager.load_data()
    app.choreManager.reassign_all_chores()
    app.choreService = ChoreService(app.choreManager)
    app.userService = UserService(app.choreManager)
    app.LeaderboardService = LeaderboardService(app.choreManager)
    app.SummaryService = SummaryService(app.choreManager)
    app.EmailService = EmailService(mail)

    # Register blueprints
    from Frontend.routes.main_routes import main_bp
    from Frontend.routes.leaderboard_routes import leaderboard_bp
    from Frontend.routes.auth_routes import auth_bp
    from Frontend.routes.user_mng_routes import user_mng_bp
    from Frontend.routes.user_chores import user_chores_bp
    from Frontend.routes.chores_routes import chores_bp
    from Frontend.routes.admin_routes import admin_bp
    from Frontend.routes.summary_routes import summary_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(leaderboard_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_mng_bp)
    app.register_blueprint(user_chores_bp)
    app.register_blueprint(chores_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(summary_bp)

    # Setup error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    # Set up scheduler
    def send_daily_summary():
        with app.app_context():
            print("Sending daily summary email...")
            summary = app.SummaryService.get_summary()
            users = list(app.choreManager.users.values())
            app.EmailService.send_summary_email(summary, users)
            print("Daily summary email sent successfully!")

    scheduler = BackgroundScheduler()
    scheduler.add_job(send_daily_summary, 'cron',
                      hour=app.config['SUMMARY_EMAIL_HOUR'],
                      minute=app.config['SUMMARY_EMAIL_MINUTE'])
    scheduler.start()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=app.config['DEBUG'])