# -*- coding: utf-8 -*-
"""
Chore.py
Created on 05/02/2026
@author: Callum
"""
from enum import Enum
from uuid import uuid4

class RecurrenceInterval(Enum):
    DAILY = 'daily'
    WEEKLY = 'weekly'
    MONTHLY = 'monthly'
    ONCE = 'once'


class Chore:
    def __init__(self, label, difficulty, location, required_properties, recurrence_interval=RecurrenceInterval.ONCE,
                 id=None):
        self.id = id or str(uuid4())
        self.label = label
        self.difficulty = difficulty
        self.location = location
        self.required_properties = required_properties
        self.recurrence_interval = recurrence_interval

    @classmethod
    def from_dict(cls, data):
        """Load a Chore from a dictionary (e.g., from JSON)"""
        return cls(
            label=data['label'],
            difficulty=data['difficulty'],
            location=data['location'],
            required_properties=set(data['required_properties']),
            recurrence_interval=RecurrenceInterval(data['recurrence_interval']),
            id=data.get('id')
        )

    def to_dict(self):
        """Convert Chore to dictionary (for JSON serialization)"""
        return {
            'id': self.id,
            'label': self.label,
            'difficulty': self.difficulty,
            'location': self.location,
            'required_properties': list(self.required_properties),
            'recurrence_interval': self.recurrence_interval.value
        }