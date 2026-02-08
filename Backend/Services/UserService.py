# -*- coding: utf-8 -*-
"""
UserService.py
Created on 06/02/2026
@author: Callum
"""
from werkzeug.security import generate_password_hash, check_password_hash
from Backend.Managers.User import User
from Backend.Managers.ChoreManager import ChoreManager
from Backend.Managers.ChoreInstance import ChoreStatus


class UserService:
    """Handles user-related operations"""

    def __init__(self, chore_manager):
        self.manager = chore_manager


    def authenticate(self, email, password):
        """Check credentials, return user or None"""
        user = next((u for u in self.manager.users.values() if u.email == email), None)

        if user and check_password_hash(user.password_hash, password):
            return user

        return None

    def create_user(self, name, email, password, properties):
        """Create a new user with hashed password"""
        # Check if email already exists
        if any(u.email == email for u in self.manager.users.values()):
            raise ValueError(f"User with email {email} already exists")

        user = User.create_new(name, email, password, properties)
        self.manager.users[user.id] = user
        self.manager.save_data()
        self.manager.instances = {}
        self.manager.reassign_all_chores()
        return user

    def get_user(self, user_id):
        """Fetch a user by ID"""
        self.manager.reassign_all_chores()
        return self.manager.users.get(user_id)

    def get_all_users(self):
        """List all users"""
        self.manager.reassign_all_chores()
        return list(self.manager.users.values())

    def update_user_properties(self, user_id, properties):
        """Update a user's properties"""
        self.manager.reassign_all_chores()
        user = self.manager.users.get(user_id)

        if not user:
            raise ValueError(f"User {user_id} not found")

        # Merge new properties with existing ones
        user.properties.update(properties)
        self.manager.save_data()
        self.manager.reassign_all_chores()
        return user

    def get_user_chores(self, user_id):
        """Get all instances assigned to a user (pending and completed)"""
        from datetime import date

        user = self.manager.users.get(user_id)

        if not user:
            raise ValueError(f"User {user_id} not found")

        # Get both pending AND completed instances
        user_instances = [inst for inst in self.manager.instances.values()
                          if inst.assigned_to == user_id]

        # Enrich with chore details
        chores_with_details = []
        for instance in user_instances:
            chore = self.manager.chores[instance.chore_id]

            # Determine status: overdue if pending and past due date
            status = instance.status.value
            if instance.status == ChoreStatus.PENDING and instance.due_date < date.today():
                status = ChoreStatus.OVERDUE.value

            chores_with_details.append({
                'instance_id': instance.id,
                'chore_id': chore.id,
                'label': chore.label,
                'difficulty': chore.difficulty,
                'location': chore.location,
                'due_date': instance.due_date.isoformat(),
                'status': status
            })
        self.manager.reassign_all_chores()
        return chores_with_details