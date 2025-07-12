from flask import Blueprint, render_template, request, redirect, url_for
from ..models import Project
from .. import db

project_bp = Blueprint('projects', __name__)

@project_bp.route('/projects', methods=['GET', 'POST'])
def projects():
    if request.method == 'POST':
        name = request.form['name']
        db.session.add(Project(name=name))
        db.session.commit()
        return redirect(url_for('projects.projects'))

    all_projects = Project.query.all()
    return render_template('projects.html', projects=all_projects)
