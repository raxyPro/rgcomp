from flask import Flask, request, render_template, send_from_directory, redirect, url_for
import os
import shutil
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)

ALLOWED_EXTENSIONS = {
    'image': ['.png', '.jpg', '.jpeg', '.gif'],
    'pdf': ['.pdf'],
    'text': ['.txt', '.log'],
    'word': ['.doc', '.docx'],
    'excel': ['.xls', '.xlsx'],
    'ppt': ['.ppt', '.pptx'],
    'video': ['.mp4', '.webm']
}

@app.template_filter('datetimeformat')
def datetimeformat(value):
    return datetime.fromtimestamp(value).strftime('%Y-%m-%d %H:%M:%S')

def detect_filetype(filename):
    ext = os.path.splitext(filename)[1].lower()
    for filetype, extensions in ALLOWED_EXTENSIONS.items():
        if ext in extensions:
            return filetype
    return 'other'

@app.route('/', methods=['GET', 'POST'])
def index():
    directory = request.form.get('directory') or request.args.get('dir') or ''
    selected_file = request.args.get('file')
    files = []

    if directory and os.path.isdir(directory):
        files = sorted([f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))])
    else:
        directory = ''

    file_url = filetype = content = prev_file = next_file = file_stat = None

    if selected_file and directory and selected_file in files:
        full_path = os.path.join(directory, selected_file)
        if os.path.isfile(full_path):
            filetype = detect_filetype(selected_file)
            file_url = url_for('serve_file', dir=directory, filename=selected_file)

            if filetype in ['text', 'html']:
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

            file_stat = os.stat(full_path)

            index = files.index(selected_file)
            prev_file = files[index - 1] if index > 0 else None
            next_file = files[index + 1] if index < len(files) - 1 else None

    return render_template('index.html', directory=directory, files=files, file=selected_file,
                           file_url=file_url, filetype=filetype, content=content,
                           prev_file=prev_file, next_file=next_file, file_stat=file_stat, os=os)

@app.route('/view')
def view_file():
    return redirect(url_for('index', dir=request.args.get('dir'), file=request.args.get('file')))

@app.route('/delete', methods=['POST'])
def delete_file():
    directory = request.args.get('dir')
    filename = request.args.get('file')

    if directory and filename:
        full_path = os.path.join(directory, filename)
        deleted_folder = os.path.join(directory, "deleted")
        os.makedirs(deleted_folder, exist_ok=True)

        deleted_path = os.path.join(deleted_folder, filename)
        if os.path.exists(full_path):
            shutil.move(full_path, deleted_path)

        remaining_files = sorted([f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))])
        if filename in remaining_files:
            remaining_files.remove(filename)

        if remaining_files:
            try:
                next_index = remaining_files.index(filename)
                next_file = remaining_files[next_index] if next_index < len(remaining_files) else remaining_files[0]
            except ValueError:
                next_file = remaining_files[0]
            return redirect(url_for('index', dir=directory, file=next_file))

    return redirect(url_for('index', dir=directory))

@app.route('/file')
def serve_file():
    directory = request.args.get('dir')
    filename = request.args.get('filename')
    if directory and filename:
        return send_from_directory(directory, filename)
    return '', 404

if __name__ == '__main__':
    app.run(debug=True)
