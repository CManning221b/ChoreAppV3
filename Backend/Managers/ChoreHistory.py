# -*- coding: utf-8 -*-
"""
ChoreHistory.py
Created on 17/02/2026
@author: Callum
"""

# -*- coding: utf-8 -*-
"""
ChoreHistory.py
Created on 17/02/2026
@author: Callum
"""

from datetime import datetime
import uuid

class ChoreHistoryEntry:
    """Represents a single chore completion event"""

    def __init__(self, user_id, user_name, chore_id, chore_name, timestamp=None, entry_id=None):
        self.id = entry_id or str(uuid.uuid4())
        self.user_id = user_id  # Who completed it
        self.user_name = user_name
        self.chore_id = chore_id
        self.chore_name = chore_name
        self.timestamp = timestamp or datetime.now()

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user_name,
            'chore_id': self.chore_id,
            'chore_name': self.chore_name,
            'timestamp': self.timestamp.isoformat()
        }

    @staticmethod
    def from_dict(data):
        return ChoreHistoryEntry(
            user_id=data['user_id'],
            user_name=data['user_name'],
            chore_id=data['chore_id'],
            chore_name=data['chore_name'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            entry_id=data['id']
        )