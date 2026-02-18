# -*- coding: utf-8 -*-
"""
ChoreAssigner.py
Created on 05/02/2026
@author: Callum
"""
from datetime import datetime, timedelta

from Backend.Managers.ChoreInstance import ChoreInstance, ChoreStatus
from Backend.Managers.Chore import Chore, RecurrenceInterval
from Backend.Managers.User import User

import random
import json

class ChoreAssigner:
    """Handles auto-assignment logic"""

    def __init__(self, users, chores, instances, recently_assigned_file_path):
        self.users = users
        self.chores = chores
        self.instances = instances
        self.recently_assigned_file_path = recently_assigned_file_path
        self.recent_history = {}
        self._load_recent_history()

    def _load_recent_history(self):
        """Load recent history from file"""
        try:
            with open(self.recently_assigned_file_path) as f:
                content = f.read().strip()
                self.recent_history = json.loads(content) if content else {}
        except FileNotFoundError:
            self.recent_history = {}

    def _save_recent_history(self):
        """Save recent history to file"""
        with open(self.recently_assigned_file_path, 'w') as f:
            json.dump(self.recent_history, f, indent=2)

    def _update_recent_history(self):
        """Rebuild recent_history dict from current instances and save to file"""
        self.recent_history = {}
        for instance in self.instances.values():
            self.recent_history[instance.chore_id] = instance.assigned_to
        self._save_recent_history()

    def assign_chore(self, chore_id, user_id=None):
        """Assign a chore. If user_id is None, auto-pick best candidate."""
        chore = self.chores[chore_id]

        if user_id is None:
            user = self._find_best_candidate(chore)
        else:
            user = self.users[user_id]

        if not user.can_do_chore(chore):
            raise ValueError(f"{user.name} can't do {chore.label}")

        due_date = self._calculate_due_date(chore)
        instance = ChoreInstance(
            chore_id=chore_id,
            assigned_to=user.id,
            due_date=due_date
        )
        self.instances[instance.id] = instance

        # Update recent history
        self.recent_history[chore_id] = user.id
        self._save_recent_history()

        return instance

    def delete_instance(self, instance_id):
        """Remove a chore instance"""
        del self.instances[instance_id]


    def _get_chores_without_instances(self):
        chores_with_any_instance = set(inst.chore_id for inst in self.instances.values())

        return [chore_id for chore_id in self.chores.keys()
                if chore_id not in chores_with_any_instance]

    def assign_all_chores(self):
        """Clean up completed/overdue instances, then assign all chores without instances"""
        today = datetime.now().date()

        self._update_recent_history()

        instances_to_delete = [
            inst_id for inst_id, inst in self.instances.items()
            if (inst.status == ChoreStatus.COMPLETE and inst.due_date <= today)
        ]

        for inst_id in instances_to_delete:
            self.delete_instance(inst_id)

        chores_to_assign = self._get_chores_without_instances()
        for chore_id in chores_to_assign:
            self.assign_chore(chore_id)

    def _find_best_candidate(self, chore):
        """Pick user. Prefer: not recently assigned, then fewest pending, then lowest points"""
        eligible = [u for u in self.users.values() if u.can_do_chore(chore)]
        eligible = random.sample(eligible, k=len(eligible))

        if not eligible:
            raise ValueError(f"No users can do {chore.label}")

        # Filter out who recently did this chore
        last_assignee_id = self.recent_history.get(chore.id)
        if last_assignee_id:
            others = [u for u in eligible if u.id != last_assignee_id]
            if others:
                eligible = others

        # Pick by fewest pending chores (primary), then lowest points (secondary)
        return min(eligible, key=lambda u: (self._total_assigned_count(u.id), u.points))

    def _pending_count(self, user_id):
        """Count pending chores for a user"""
        return sum(1 for inst in self.instances.values()
                   if inst.assigned_to == user_id and inst.status == ChoreStatus.PENDING)

    def _total_assigned_count(self, user_id):
        return sum(1 for inst in self.instances.values()
                   if inst.assigned_to == user_id)

    def _calculate_due_date(self, chore):
        """Calculate due date based on recurrence interval"""
        today = datetime.now().date()
        if chore.recurrence_interval == RecurrenceInterval.DAILY:
            return today
        elif chore.recurrence_interval == RecurrenceInterval.WEEKLY:
            return today + timedelta(weeks=1)
        elif chore.recurrence_interval == RecurrenceInterval.MONTHLY:
            return today + timedelta(days=30)
        else:  # ONCE
            return today + timedelta(days=7)