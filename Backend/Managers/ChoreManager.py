# -*- coding: utf-8 -*-
"""
ChoreManager.py
Created on 05/02/2026
@author: Callum
"""
import json
from datetime import datetime

from Backend.Managers.ChoreAssigner import ChoreAssigner
from Backend.Managers.User import User
from Backend.Managers.Chore import Chore, RecurrenceInterval
from Backend.Managers.ChoreInstance import ChoreInstance, ChoreStatus
from Backend.Managers.ChoreHistory import ChoreHistoryEntry

POINTSVALUE = 10

class ChoreManager:
    """Main orchestrator - handles persistence, state, operations"""

    def __init__(self, users_file='users.json', chores_file='chores.json', instances_file='instances.json', history_file = 'history.json', recently_assigned_file = 'recentlyAssigned.json'):
        self.users_file = users_file
        self.chores_file = chores_file
        self.instances_file = instances_file
        self.history_file = history_file
        self.recently_assigned_file = recently_assigned_file

        self.users = {}
        self.chores = {}
        self.instances = {}
        self.chore_histroy = []
        self.assigner = None

        self.load_data()

    def load_data(self):
        """Load from three separate JSON files"""
        try:
            with open(self.users_file) as f:
                content = f.read().strip()
                users_data = json.loads(content) if content else []
                self.users = {u['id']: User.from_dict(u) for u in users_data}
        except FileNotFoundError:
            self.users = {}

        try:
            with open(self.chores_file) as f:
                content = f.read().strip()
                chores_data = json.loads(content) if content else []
                self.chores = {c['id']: Chore.from_dict(c) for c in chores_data}
        except FileNotFoundError:
            self.chores = {}

        try:
            with open(self.instances_file) as f:
                content = f.read().strip()
                instances_data = json.loads(content) if content else []
                self.instances = {i['id']: ChoreInstance.from_dict(i) for i in instances_data}
        except FileNotFoundError:
            self.instances = {}

        try:
            with open(self.history_file) as f:
                content = f.read().strip()
                history_data = json.loads(content) if content else []
                self.chore_history = [ChoreHistoryEntry.from_dict(h) for h in history_data]
        except FileNotFoundError:
            self.chore_history = []

        self.assigner = ChoreAssigner(self.users, self.chores, self.instances, self.recently_assigned_file)

    def save_data(self):
        """Write to three separate JSON files"""
        with open(self.users_file, 'w') as f:
            json.dump([u.to_dict() for u in self.users.values()], f, indent=2)

        with open(self.chores_file, 'w') as f:
            json.dump([c.to_dict() for c in self.chores.values()], f, indent=2)

        with open(self.instances_file, 'w') as f:
            json.dump([i.to_dict() for i in self.instances.values()], f, indent=2)

        with open(self.history_file, 'w') as f:
            json.dump([h.to_dict() for h in self.chore_history], f, indent=2)

    def complete_chore(self, instance_id):
        """Mark instance as done, award points, reassign recurring chores"""
        instance = self.instances[instance_id]
        chore = self.chores[instance.chore_id]
        user = self.users[instance.assigned_to]

        instance.status = ChoreStatus.COMPLETE
        instance.completed_date = datetime.now().date()
        user.points += chore.difficulty * POINTSVALUE

        # Log the completion
        entry = ChoreHistoryEntry(
            user_id=user.id,
            user_name=user.name,
            chore_id=chore.id,
            chore_name=chore.label
        )
        self.chore_history.append(entry)

        self.reassign_all_chores()

    def swap_chore(self, chore_id, user_id_1, user_id_2):
        """Swap a specific chore between two users"""
        # Find the instance of this chore assigned to user_id_1
        instance = next((i for i in self.instances.values()
                         if i.chore_id == chore_id and i.assigned_to == user_id_1
                         and i.status == ChoreStatus.PENDING), None)

        if not instance:
            raise ValueError(f"No pending instance of chore {chore_id} assigned to user {user_id_1}")

        user1 = self.users[user_id_1]
        user2 = self.users[user_id_2]
        chore = self.chores[chore_id]

        if not user2.can_do_chore(chore):
            raise ValueError(f"{user2.name} can't do {chore.label}")

        instance.assigned_to = user_id_2
        self.save_data()

    def reset_points_if_month_start(self):
        """Reset all users' points if it's the first of the month"""
        today = datetime.now().date()
        if today.day == 1:
            for user in self.users.values():
                user.points = 0
            self.save_data()

    def reassign_all_chores(self):
        """Reassign all chores (cleanup + assign new)"""
        self.reset_points_if_month_start()
        self.assigner._update_recent_history()  # Ensure history is current
        self.assigner.assign_all_chores()
        self.save_data()

