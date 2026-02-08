# -*- coding: utf-8 -*-
"""
User.py
Created on 05/02/2026
@author: Callum
"""
from uuid import uuid4
from werkzeug.security import generate_password_hash, check_password_hash


class User:
    def __init__(self, name: str = "", email: str = "", password_hash = None, properties = {}, id=None, points = 0):
        self.id = id or str(uuid4())
        self.name = name
        self.email = email
        self.password_hash = password_hash
        self.properties = properties
        self.points = points

    def can_do_chore(self, chore):
        """Check if user has all required properties for a chore"""
        return all(self.properties.get(prop) for prop in chore.required_properties)

    def check_password(self, password):
        """Verify a plaintext password against the hash"""
        return check_password_hash(self.password_hash, password)

    @classmethod
    def from_dict(cls, data):
        """Load a User from a dictionary (e.g., from JSON)"""
        return cls(
            name=data['name'],
            email=data['email'],
            password_hash=data['password_hash'],
            properties=data['properties'],
            id=data.get('id'),
            points=data.get('points', 0)  # Add this
        )

    def to_dict(self):
        """Convert User to dictionary (for JSON serialization)"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'password_hash': self.password_hash,
            'properties': self.properties,
            'points': self.points
        }

    @classmethod
    def create_new(cls, name, email, plaintext_password, properties):
        """Create a new user with a hashed password"""
        password_hash = generate_password_hash(plaintext_password)
        return cls(name, email, password_hash, properties)

