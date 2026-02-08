# -*- coding: utf-8 -*-
"""
tst_managers.py
Created on 05/02/2026
@author: Callum
"""
# test_chores.py
from ChoreManager import ChoreManager

# Initialize manager
manager = ChoreManager('../../Data/users.json', '../../Data/chores.json', '../../Data/instances.json')
manager.load_data()

print("=== Initial State ===")
print(f"Users: {len(manager.users)}")
print(f"Chores: {len(manager.chores)}")
print(f"Instances: {len(manager.instances)}")

print("\n=== Assigning all chores ===")
manager.reassign_all_chores()

print(f"Instances after assignment: {len(manager.instances)}")
for inst_id, instance in manager.instances.items():
    chore = manager.chores[instance.chore_id]
    user = manager.users[instance.assigned_to]
    print(f"  {chore.label} -> {user.name} (due: {instance.due_date})")

print("\n=== Complete a chore ===")
first_instance_id = list(manager.instances.keys())[0]
first_instance = manager.instances[first_instance_id]
chore = manager.chores[first_instance.chore_id]
user = manager.users[first_instance.assigned_to]
print(f"Completing: {chore.label} (assigned to {user.name})")
manager.complete_chore(first_instance_id)
print(f"{user.name} now has {user.points} points")

print(f"\nInstances after completion: {len(manager.instances)}")
for inst_id, instance in manager.instances.items():
    chore = manager.chores[instance.chore_id]
    user = manager.users[instance.assigned_to]
    print(f"  {chore.label} -> {user.name}")

print("\n=== Swap a chore ===")
# Get the "hoover" chore instance
hoover_instances = [i for i in manager.instances.values() if manager.chores[i.chore_id].label == "Hoover downstairs"]
if hoover_instances:
    hoover_inst = hoover_instances[0]
    current_user = manager.users[hoover_inst.assigned_to]
    other_user = next(
        (u for u in manager.users.values() if u.id != hoover_inst.assigned_to and u.properties.get("can_lift")), None)

    if other_user:
        print(f"Swapping 'Hoover downstairs' from {current_user.name} to {other_user.name}")
        manager.swap_chore("chore_2", current_user.id, other_user.id)

        print(f"After swap:")
        for inst_id, instance in manager.instances.items():
            chore = manager.chores[instance.chore_id]
            user = manager.users[instance.assigned_to]
            print(f"  {chore.label} -> {user.name}")

print("\n=== Leaderboard ===")
sorted_users = sorted(manager.users.values(), key=lambda u: u.points, reverse=True)
for i, user in enumerate(sorted_users, 1):
    print(f"{i}. {user.name}: {user.points} points")