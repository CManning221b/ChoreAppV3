# -*- coding: utf-8 -*-
"""
SummaryService.py
Created on 18/02/2026
@author: Callum
"""
from Backend.Services.ChoreService import ChoreService
from Backend.Services.UserService import UserService
from Backend.Services.LeaderboardService import LeaderboardService

from Backend.Managers.ChoreManager import ChoreManager
from Backend.Managers.ChoreAssigner import ChoreAssigner
from Backend.Managers.ChoreInstance import ChoreStatus

from datetime import datetime, timedelta

class SummaryService:
    """Collates high-level summary data for dashboard display"""

    def __init__(self, chore_manager):
        self.manager = chore_manager
        self.chore_service = ChoreService(chore_manager)
        self.user_service = UserService(chore_manager)
        self.leaderboard_service = LeaderboardService(chore_manager)

    def get_summary(self):
        """Return a full summary snapshot"""
        self._update_overdue_statuses()

        return {
            'leader': self._get_leader(),
            'most_overdue': self._get_most_overdue_user(),
            'current_chores': self._get_current_chores_by_user(),
            'completed_last_24h': self._get_completed_last_24h()
        }

    def _get_leader(self):
        """Return the user currently in first place"""
        leaderboard = self.leaderboard_service.get_leaderboard()
        if not leaderboard:
            return None
        return leaderboard[0]  # Already sorted by points descending

    def _get_most_overdue_user(self):
        """Return the user with the most overdue chores"""
        overdue_counts = {}

        for inst in self.manager.instances.values():
            if inst.status == ChoreStatus.OVERDUE:
                overdue_counts[inst.assigned_to] = overdue_counts.get(inst.assigned_to, 0) + 1

        if not overdue_counts:
            return None

        top_user_id = max(overdue_counts, key=overdue_counts.get)
        user = self.manager.users[top_user_id]

        return {
            'user_id': user.id,
            'name': user.name,
            'overdue_count': overdue_counts[top_user_id]
        }

    def _get_current_chores_by_user(self):
        """Return each user's currently assigned chores (pending + overdue)"""
        summary = {}

        for user in self.manager.users.values():
            user_instances = [
                inst for inst in self.manager.instances.values()
                if inst.assigned_to == user.id
                and inst.status in (ChoreStatus.PENDING, ChoreStatus.OVERDUE)
            ]

            chores = []
            for inst in user_instances:
                chore = self.manager.chores[inst.chore_id]
                chores.append({
                    'instance_id': inst.id,
                    'label': chore.label,
                    'due_date': inst.due_date.strftime('%d/%m/%Y'),
                    'status': inst.status.value
                })

            summary[user.id] = {
                'name': user.name,
                'chores': chores
            }

        return summary

    def _update_overdue_statuses(self):
        from datetime import date
        needs_save = False
        for inst in self.manager.instances.values():
            if inst.status == ChoreStatus.PENDING and inst.due_date < date.today():
                inst.status = ChoreStatus.OVERDUE
                needs_save = True
        if needs_save:
            self.manager.save_data()

    def _get_completed_last_24h(self):
        """Return chore completions in the last 24 hours from history"""
        cutoff = datetime.now() - timedelta(hours=24)

        recent = [
            entry for entry in self.manager.chore_history
            if entry.timestamp >= cutoff
        ]

        return [
            {
                'user_name': entry.user_name,
                'chore_name': entry.chore_name,
                'timestamp': entry.timestamp.strftime('%d/%m/%Y %H:%M')
            }
            for entry in sorted(recent, key=lambda e: e.timestamp, reverse=True)
        ]