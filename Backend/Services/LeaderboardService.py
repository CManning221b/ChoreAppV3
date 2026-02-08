# -*- coding: utf-8 -*-
"""
LeaderboardService.py
Created on 06/02/2026
@author: Callum
"""

from Backend.Managers.ChoreInstance import ChoreStatus
from Backend.Managers.ChoreManager import ChoreManager


class LeaderboardService:
    """Handles leaderboard and statistics"""

    def __init__(self, chore_manager):
        self.manager = chore_manager

    def get_leaderboard(self):
        """Return sorted list of users by points (descending)"""
        users = list(self.manager.users.values())
        sorted_users = sorted(users, key=lambda u: u.points, reverse=True)

        leaderboard = []
        for rank, user in enumerate(sorted_users, 1):
            leaderboard.append({
                'rank': rank,
                'user_id': user.id,
                'name': user.name,
                'points': user.points
            })
        self.manager.reassign_all_chores()
        return leaderboard

    def get_user_stats(self, user_id):
        """Return stats for a specific user"""
        user = self.manager.users.get(user_id)

        if not user:
            raise ValueError(f"User {user_id} not found")

        # Count pending and completed instances
        user_instances = [inst for inst in self.manager.instances.values()
                          if inst.assigned_to == user_id]

        pending_count = sum(1 for inst in user_instances if inst.status == ChoreStatus.PENDING)
        completed_count = sum(1 for inst in user_instances if inst.status == ChoreStatus.COMPLETE)

        # Get rank in leaderboard
        all_users = sorted(self.manager.users.values(), key=lambda u: u.points, reverse=True)
        rank = next((i + 1 for i, u in enumerate(all_users) if u.id == user_id), None)
        self.manager.reassign_all_chores()
        return {
            'user_id': user.id,
            'name': user.name,
            'points': user.points,
            'rank': rank,
            'pending_chores': pending_count,
            'completed_chores': completed_count,
            'total_chores': pending_count + completed_count
        }

    def get_chore_stats(self, chore_id):
        """Return stats for a specific chore"""
        chore = self.manager.chores.get(chore_id)

        if not chore:
            raise ValueError(f"Chore {chore_id} not found")

        # Get all instances of this chore
        chore_instances = [inst for inst in self.manager.instances.values()
                           if inst.chore_id == chore_id]

        completed = [inst for inst in chore_instances if inst.status == ChoreStatus.COMPLETE]
        pending = [inst for inst in chore_instances if inst.status == ChoreStatus.PENDING]

        # Track who's been assigned it (including history)
        assigned_users = {}
        for instance in chore_instances:
            user = self.manager.users[instance.assigned_to]
            if user.id not in assigned_users:
                assigned_users[user.id] = {'name': user.name, 'count': 0}
            assigned_users[user.id]['count'] += 1

        completion_rate = len(completed) / len(chore_instances) if chore_instances else 0
        self.manager.reassign_all_chores()
        return {
            'chore_id': chore.id,
            'label': chore.label,
            'difficulty': chore.difficulty,
            'recurrence_interval': chore.recurrence_interval.value,
            'total_instances': len(chore_instances),
            'completed_count': len(completed),
            'pending_count': len(pending),
            'completion_rate': round(completion_rate, 2),
            'assigned_to': assigned_users
        }
