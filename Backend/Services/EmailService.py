# -*- coding: utf-8 -*-
"""
EmailService.py
Created on 18/02/2026
@author: Callum
"""

from flask import render_template
from flask_mail import Mail, Message
from premailer import transform
import os

from Frontend.config import PROJECT_ROOT

class EmailService:
    def __init__(self, mail: Mail):
        self.mail = mail

    def send_summary_email(self, summary, users):
        recipients = [u.email for u in users]

        static_dir = os.path.join(PROJECT_ROOT, 'Frontend', 'static', 'css')
        with open(os.path.join(static_dir, 'main.css')) as f:
            base_css = f.read()
        with open(os.path.join(static_dir, 'summary.css')) as f:
            summary_css = f.read()

        html_body = render_template('summary/summary_email.html', summary=summary,
                                    base_css=base_css, summary_css=summary_css)
        html_body = transform(html_body)

        msg = Message(
            subject="Team Manning — Daily Chore Summary",
            recipients=recipients,
            html=html_body
        )

        self.mail.send(msg)