# -*- coding: utf-8 -*-
"""
admin_routes.py
Created on 08/02/2026
@author: Callum
"""
from flask import current_app, Blueprint, render_template, session, request, redirect, url_for
from Backend.Services.UserService import UserService
from Backend.Managers.ChoreInstance import ChoreStatus
from utils.decorators import login_required, admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/', methods=['GET'])
@admin_required
@login_required
def get_chores_admin():
    chores = current_app.choreManager.chores
    chore_id = request.args.get('chore_id')
    chore = chores.get(chore_id) if chore_id else None
    return render_template('admin/chores_manager.html', chores=chores, chore=chore, chore_id=chore_id)

@admin_bp.route('/', methods=['POST'])
@admin_required
@login_required
def update_chores_admin():
    # POST - chore details
    chore_id = request.form.get('chore_id')
    label = request.form.get('label')
    dificulty = int(request.form.get('dificulty'))
    location = request.form.get('location')
    recurrence_interval = request.form.get('recurrence_interval')
    exclude_keys = {'label', 'dificulty', 'location', 'recurrence_interval', 'chore_id'}
    required_properties = [key for key, value in request.form.items()
                           if key not in exclude_keys and value == 'on']
    try:
        if chore_id:
            chore = current_app.choreService.update_chore(chore_id, label, dificulty, location,
                                                          required_properties, recurrence_interval)
        else:
            chore = current_app.choreService.create_chore(label, dificulty, location,
                                                          required_properties, recurrence_interval)
        return redirect(url_for('admin.get_chores_admin'))
    except ValueError as e:
        chores = current_app.choreManager.chores
        chore = current_app.choreManager.chores.get(chore_id) if chore_id else None
        return render_template('admin/chores_manager.html', chores=chores, chore=chore,
                              chore_id=chore_id, error=str(e))

@admin_bp.route('/users', methods=['GET'])
@admin_required
@login_required
def get_person_details_admin():
    users = current_app.choreManager.users
    user_id = request.args.get('user_id')
    user = users.get(user_id) if user_id else None
    return render_template('admin/user_manager.html', users=users, user=user, user_id=user_id)


@admin_bp.route('/users', methods=['POST'])
@admin_required
@login_required
def update_person_admin():
    user_id = request.form.get('user_id')
    points = request.form.get('points')
    exclude_keys = {'user_id', 'points'}
    user_properties = {key: value == 'on' for key, value in request.form.items()
                       if key not in exclude_keys}
    try:
        if user_id:
            user = current_app.userService.update_user_properties(user_id, user_properties)
            if points:
                user.points = int(points)
                current_app.choreManager.save_data()
            return redirect(url_for('admin.get_person_details_admin', user_id=user_id))
    except ValueError as e:
        users = current_app.choreManager.users
        user = users.get(user_id)
        return render_template('admin/user_manager.html', users=users, user=user, user_id=user_id, error=str(e))


@admin_bp.route('/instances', methods=['GET'])
@admin_required
@login_required
def get_chore_instance_details_admin():
    instances = current_app.choreManager.instances
    chores = current_app.choreManager.chores
    users = current_app.choreManager.users
    instance_id = request.args.get('instance_id')
    instance = instances.get(instance_id) if instance_id else None
    return render_template('admin/instance_manager.html', instances=instances, instance=instance,
                           instance_id=instance_id, chores=chores, users=users)


@admin_bp.route('/instances', methods=['POST'])
@admin_required
@login_required
def update_chore_instance_details_admin():
    instance_id = request.form.get('instance_id')
    assigned_to = request.form.get('assigned_to')
    status = request.form.get('status')

    try:
        if instance_id:
            instance = current_app.choreManager.instances.get(instance_id)
            if not instance:
                raise ValueError(f"Instance {instance_id} not found")

            user = current_app.choreManager.users.get(assigned_to)
            if not user:
                raise ValueError(f"User {assigned_to} not found")

            chore = current_app.choreManager.chores.get(instance.chore_id)
            if not user.can_do_chore(chore):
                raise ValueError(f"{user.name} can't do {chore.label}")

            instance.assigned_to = assigned_to
            instance.status = ChoreStatus(status)
            current_app.choreManager.save_data()
            current_app.choreManager.reassign_all_chores()
            return redirect(url_for('admin.get_chore_instance_details_admin', instance_id=instance_id))
    except ValueError as e:
        instances = current_app.choreManager.instances
        chores = current_app.choreManager.chores
        users = current_app.choreManager.users
        instance = instances.get(instance_id)
        return render_template('admin/instance_manager.html', instances=instances, instance=instance,
                               instance_id=instance_id, chores=chores, users=users, error=str(e))


@admin_bp.route('/instances/<instance_id>/delete', methods=['POST'])
@admin_required
@login_required
def delete_chore_instance_admin(instance_id):
    try:
        current_app.choreService.delete_instance(instance_id)
        return redirect(url_for('admin.get_chore_instance_details_admin'))
    except ValueError as e:
        instances = current_app.choreManager.instances
        chores = current_app.choreManager.chores
        users = current_app.choreManager.users
        return render_template('admin/instance_manager.html', instances=instances,
                               chores=chores, users=users, error=str(e))