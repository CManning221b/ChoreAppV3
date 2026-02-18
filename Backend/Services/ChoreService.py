# -*- coding: utf-8 -*-
"""
ChoreService.py
Created on 06/02/2026
@author: Callum
"""
from Backend.Managers.Chore import Chore, RecurrenceInterval
from Backend.Managers.ChoreInstance import ChoreStatus
from Backend.Managers.ChoreManager import ChoreManager

class ChoreService:
    """Handles chore-related operations"""

    def __init__(self, chore_manager):
        self.manager = chore_manager

    def get_all_chores(self):
        """List all chore templates"""
        self.manager.reassign_all_chores()
        return list(self.manager.chores.values())

    def get_all_chores_instances(self):
        """Get all chore instances with user and chore details"""
        chores_data = []

        for instance in self.manager.instances.values():
            chore = self.manager.chores[instance.chore_id]
            user = self.manager.users[instance.assigned_to]

            chores_data.append({
                'user_name': user.name,
                'chore_name': chore.label,
                'status': instance.status.value
            })
        self.manager.reassign_all_chores()
        return chores_data

    def create_chore(self, label, difficulty, location, required_properties, recurrence_interval='weekly'):
        """Create a new chore template"""
        # Convert string to RecurrenceInterval enum if needed
        if isinstance(recurrence_interval, str):
            recurrence_interval = RecurrenceInterval(recurrence_interval)

        chore = Chore(
            label=label,
            difficulty=difficulty,
            location=location,
            required_properties=set(required_properties),
            recurrence_interval=recurrence_interval
        )

        self.manager.chores[chore.id] = chore
        self.manager.save_data()
        self.manager.reassign_all_chores()
        return chore

    def create_instance(self, chore_id, user_id):
        """Manually assign a chore to a user (admin only)"""
        if chore_id not in self.manager.chores:
            raise ValueError(f"Chore {chore_id} not found")
        if user_id not in self.manager.users:
            raise ValueError(f"User {user_id} not found")

        chore = self.manager.chores[chore_id]
        user = self.manager.users[user_id]

        if not user.can_do_chore(chore):
            raise ValueError(f"{user.name} can't do {chore.label}")

        existing = next((i for i in self.manager.instances.values()
                         if i.chore_id == chore_id and i.assigned_to == user_id
                         and i.status == ChoreStatus.PENDING), None)
        if existing:
            raise ValueError(f"{user.name} already has a pending instance of {chore.label}")

        instance = self.manager.assigner.assign_chore(chore_id, user_id)
        self.manager.save_data()
        self.manager.reassign_all_chores()
        return instance

    def delete_instance(self, instance_id):
        """Delete a chore instance (admin only)"""
        if instance_id not in self.manager.instances:
            raise ValueError(f"Instance {instance_id} not found")
        self.manager.assigner.delete_instance(instance_id)
        self.manager.save_data()
        self.manager.reassign_all_chores()

    def delete_chore(self, chore_id):
        """Delete a chore template and all its instances (admin only)"""
        if chore_id not in self.manager.chores:
            raise ValueError(f"Chore {chore_id} not found")

        instances_to_delete = [i_id for i_id, i in self.manager.instances.items()
                               if i.chore_id == chore_id]
        for i_id in instances_to_delete:
            self.manager.assigner.delete_instance(i_id)
        del self.manager.chores[chore_id]
        self.manager.save_data()
        self.manager.reassign_all_chores()

    def update_chore(self, chore_id, label=None, difficulty=None, location=None,
                     required_properties=None, recurrence_interval=None):
        """Update a chore template"""
        chore = self.manager.chores.get(chore_id)

        if not chore:
            raise ValueError(f"Chore {chore_id} not found")

        if label is not None:
            chore.label = label
        if difficulty is not None:
            chore.difficulty = difficulty
        if location is not None:
            chore.location = location
        if required_properties is not None:
            chore.required_properties = set(required_properties)
        if recurrence_interval is not None:
            if isinstance(recurrence_interval, str):
                recurrence_interval = RecurrenceInterval(recurrence_interval)
            chore.recurrence_interval = recurrence_interval

        self.manager.save_data()
        self.manager.reassign_all_chores()
        return chore

    def get_user_pending_chores(self, user_id):
        """Get all pending instances assigned to a user"""
        user_instances = [inst for inst in self.manager.instances.values()
                          if inst.assigned_to == user_id and inst.status == ChoreStatus.PENDING]

        # Enrich with chore details
        chores_with_details = []
        for instance in user_instances:
            chore = self.manager.chores[instance.chore_id]
            chores_with_details.append({
                'instance_id': instance.id,
                'chore_id': chore.id,
                'label': chore.label,
                'difficulty': chore.difficulty,
                'location': chore.location,
                'due_date': instance.due_date.isoformat(),
                'status': instance.status.value
            })
        self.manager.reassign_all_chores()
        return sorted(chores_with_details, key=lambda c: c['due_date'])

    def complete_chore(self, instance_id):
        """Mark a chore instance as complete"""
        if instance_id not in self.manager.instances:
            raise ValueError(f"Instance {instance_id} not found")

        self.manager.complete_chore(instance_id)
        self.manager.reassign_all_chores()

    def swap_chore(self, chore_id, user_id_1, user_id_2):
        """Swap a specific chore between two users"""
        if chore_id not in self.manager.chores:
            raise ValueError(f"Chore {chore_id} not found")
        if user_id_1 not in self.manager.users:
            raise ValueError(f"User {user_id_1} not found")
        if user_id_2 not in self.manager.users:
            raise ValueError(f"User {user_id_2} not found")

        self.manager.swap_chore(chore_id, user_id_1, user_id_2)
        self.manager.reassign_all_chores()

    def get_chore_details(self, chore_id):
        """Return chore template + all its instances"""
        chore = self.manager.chores.get(chore_id)

        if not chore:
            raise ValueError(f"Chore {chore_id} not found")

        # Get all instances of this chore
        instances = [inst for inst in self.manager.instances.values()
                     if inst.chore_id == chore_id]

        instances_data = []
        for instance in instances:
            user = self.manager.users[instance.assigned_to]
            instances_data.append({
                'instance_id': instance.id,
                'assigned_to': user.id,
                'assigned_to_name': user.name,
                'due_date': instance.due_date.isoformat(),
                'status': instance.status.value,
                'completed_date': instance.completed_date.isoformat() if instance.completed_date else None
            })
        self.manager.reassign_all_chores()
        return {
            'chore': {
                'id': chore.id,
                'label': chore.label,
                'difficulty': chore.difficulty,
                'location': chore.location,
                'required_properties': list(chore.required_properties),
                'recurrence_interval': chore.recurrence_interval.value
            },
            'instances': instances_data
        }

    def get_chore_history(self, limit=50):
        """Get recent chore completions"""
        # Return most recent first
        history = sorted(self.manager.chore_history,
                         key=lambda h: h.timestamp,
                         reverse=True)[:limit]

        return [{
            'user_name': entry.user_name,
            'chore_name': entry.chore_name,
            'timestamp': entry.timestamp.isoformat(),
            'date': entry.timestamp.strftime('%d/%m/%Y %H:%M')
        } for entry in history]