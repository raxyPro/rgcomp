from flask import Blueprint, render_template, request, redirect, url_for
from ..models import Task, Project
from .. import db
from datetime import datetime

task_bp = Blueprint('tasks', __name__)

@task_bp.route('/tasks/<int:project_id>', methods=['GET', 'POST'])
def tasks(project_id):
    project = Project.query.get_or_404(project_id)

    if request.method == 'POST':
        new_task = Task(
            description=request.form['description'],
            due_date=datetime.strptime(request.form['due_date'], '%Y-%m-%d'),
            status=request.form['status'],
            team=request.form['team'],
            project_id=project_id
        )
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('tasks.tasks', project_id=project_id))

    return render_template('tasks.html', project=project)

@task_bp.route('/edit_task/<int:id>', methods=['POST'])
def edit_task(id):
    task = Task.query.get_or_404(id)
    task.description = request.form['description']
    task.due_date = datetime.strptime(request.form['due_date'], '%Y-%m-%d')
    task.status = request.form['status']
    task.team = request.form['team']
    db.session.commit()
    return redirect(url_for('tasks.tasks', project_id=task.project_id))

@task_bp.route('/delete_task/<int:id>', methods=['POST'])
def delete_task(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('tasks.tasks', project_id=task.project_id))
