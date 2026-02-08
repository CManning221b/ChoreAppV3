# -*- coding: utf-8 -*-
"""
ChoreInstance.py
Created on 05/02/2026
@author: Callum
"""
from enum import Enum
from uuid import uuid4

class ChoreStatus(Enum):
    PENDING = 'pending'
    COMPLETE = 'complete'
    OVERDUE = 'overdue'


class ChoreInstance:
    def __init__(self, chore_id, assigned_to, due_date, status=ChoreStatus.PENDING, id=None):
        self.id = id or str(uuid4())
        self.chore_id = chore_id
        self.assigned_to = assigned_to
        self.due_date = due_date
        self.status = status
        self.completed_date = None
        self.points_awarded = 0

    @classmethod
    def from_dict(cls, data):
        from datetime import datetime
        instance = cls(
            chore_id=data['chore_id'],
            assigned_to=data['assigned_to'],
            due_date=datetime.fromisoformat(data['due_date']).date() if data.get('due_date') else None,
            status=ChoreStatus(data.get('status', 'pending')),
            id=data.get('id')
        )
        instance.completed_date = datetime.fromisoformat(data['completed_date']).date() if data.get(
            'completed_date') else None
        instance.points_awarded = data.get('points_awarded', 0)
        return instance

    def to_dict(self):
        """Convert ChoreInstance to dictionary (for JSON serialization)"""
        return {
            'id': self.id,
            'chore_id': self.chore_id,
            'assigned_to': self.assigned_to,
            'due_date': self.due_date.isoformat() if self.due_date else None,  # Convert to string
            'status': self.status.value,
            'completed_date': self.completed_date.isoformat() if self.completed_date else None,  # Also convert this
            'points_awarded': self.points_awarded
        }