# app.py
import sqlite3
from flask import Flask, render_template, request, jsonify, g, session, redirect, url_for, flash
import os
from datetime import datetime, timezone # Import datetime and timezone

app = Flask(__name__)

# Define the path for the SQLite database
DATABASE = 'database.db'

# Set a secret key for session management.
# In a production environment, this should be a strong, randomly generated key
# and loaded from an environment variable or config file.
app.secret_key = 'your_super_secret_key_here' # IMPORTANT: Change this in production!

# --- Database Initialization and Helpers ---

def get_db():
    """
    Connects to the SQLite database.
    The database connection is stored in Flask's 'g' object to be reused
    within the same request.
    """
    if 'db' not in g:
        g.db = sqlite3.connect(
            DATABASE
            # Removed 'detect_type_codes=sqlite3.PARSE_DECLTYPES' from here
            # Type detection will still work for Row objects after fetching
        )
        g.db.row_factory = sqlite3.Row  # This allows accessing columns by name
    return g.db

def close_db(e=None):
    """
    Closes the database connection at the end of the request.
    """
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """
    Initializes the database by creating necessary tables and adding default users.
    """
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.executescript(f.read())
    db.commit()
    print("Database schema initialized.")
    add_default_users() # Add default users after schema is created

def add_default_users():
    """
    Adds a few default users to the database for testing.
    This function is called during database initialization.
    """
    db = get_db()
    users_to_add = [
        ('user1', 'pass1'),
        ('user2', 'pass2'),
        ('admin', 'adminpass'),
        ('testuser', 'testpass'),
        ('guest', 'guestpass')
    ]
    try:
        for username, password in users_to_add:
            # Check if user already exists to prevent duplicates on re-init
            existing_user = db.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
            if not existing_user:
                db.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
                print(f"Added user: {username}")
        db.commit()
    except sqlite3.Error as e:
        print(f"Error adding default users: {e}")
        db.rollback()


# Register close_db to be called after each request
app.teardown_appcontext(close_db)

# Command to initialize the database from the Flask CLI
@app.cli.command('initdb')
def initdb_command():
    """Clear existing data and create new tables, then add default users."""
    init_db()
    print('Database initialized and default users added.')


# --- Routes ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handles user login.
    GET: Displays the login form.
    POST: Processes login credentials.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE username = ? AND password = ?',
            (username, password)
        ).fetchone()

        if user:
            session['logged_in'] = True
            session['username'] = user['username'] # Store username in session
            session['user_id'] = user['id']       # Store user ID in session
            flash('You were successfully logged in', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    """
    Logs out the current user by clearing the session.
    """
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('user_id', None) # Clear user ID from session
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/')
@app.route('/dashboard')
def dashboard():
    """
    Renders the main dashboard HTML page.
    Requires user to be logged in.
    """
    if not session.get('logged_in'):
        flash('Please log in to access the dashboard.', 'warning')
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session.get('username', 'User'))

# --- API Endpoints for Polling Chat ---

@app.route('/api/chat', methods=['GET'])
def get_chat_messages():
    """
    API endpoint to get all chat messages from the database.
    """
    db = get_db()
    messages = db.execute('SELECT id, sender, message, timestamp FROM chat_messages ORDER BY timestamp ASC').fetchall()
    return jsonify([dict(m) for m in messages])

@app.route('/api/chat/since/<path:timestamp_str>', methods=['GET'])
def get_chat_messages_since(timestamp_str):
    """
    API endpoint to get chat messages from the database that are newer than a given timestamp.
    The timestamp_str should be in ISO format (e.g., '2023-10-27T10:00:00.123456Z').
    """
    db = get_db()
    try:
        messages = db.execute(
            'SELECT id, sender, message, timestamp FROM chat_messages WHERE timestamp > ? ORDER BY timestamp ASC',
            (timestamp_str,)
        ).fetchall()
        return jsonify([dict(m) for m in messages])
    except Exception as e:
        print(f"Error fetching messages since timestamp: {e}")
        return jsonify({"error": "Invalid timestamp format or server error"}), 400


@app.route('/api/chat', methods=['POST'])
def add_chat_message():
    """
    API endpoint to add a new chat message to the database.
    Expects JSON payload with 'message'. Sender is taken from session.
    """
    if not session.get('logged_in'):
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    message = data.get('message')
    sender = session.get('username', 'Anonymous') # Use logged-in username as sender

    if not message:
        return jsonify({"error": "Message is required"}), 400

    db = get_db()
    try:
        cursor = db.execute(
            'INSERT INTO chat_messages (sender, message) VALUES (?, ?)',
            (sender, message)
        )
        db.commit()
        new_message = db.execute(
            'SELECT id, sender, message, timestamp FROM chat_messages WHERE id = ?',
            (cursor.lastrowid,)
        ).fetchone()
        return jsonify(dict(new_message)), 201
    except sqlite3.Error as e:
        db.rollback()
        return jsonify({"error": f"Database error: {e}"}), 500


# --- API Endpoints for Tasks (Right Column) ---

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """
    API endpoint to get all tasks for the current user from the database.
    """
    if not session.get('logged_in'):
        return jsonify({"error": "Unauthorized"}), 401

    user_id = session.get('user_id')
    db = get_db()
    tasks = db.execute('SELECT id, text, completed FROM tasks WHERE user_id = ? ORDER BY id ASC', (user_id,)).fetchall()
    return jsonify([dict(t) for t in tasks])

@app.route('/api/tasks', methods=['POST'])
def add_task():
    """
    API endpoint to add a new task for the current user to the database.
    Expects JSON payload with 'text'. 'completed' defaults to False.
    """
    if not session.get('logged_in'):
        return jsonify({"error": "Unauthorized"}), 401

    user_id = session.get('user_id')
    text = request.get_json().get('text')

    if not text:
        return jsonify({"error": "Task text is required"}), 400

    db = get_db()
    try:
        cursor = db.execute(
            'INSERT INTO tasks (user_id, text, completed) VALUES (?, ?, ?)',
            (user_id, text, False)
        )
        db.commit()
        new_task = db.execute(
            'SELECT id, text, completed FROM tasks WHERE id = ?',
            (cursor.lastrowid,)
        ).fetchone()
        return jsonify(dict(new_task)), 201
    except sqlite3.Error as e:
        db.rollback()
        return jsonify({"error": f"Database error: {e}"}), 500

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """
    API endpoint to update an existing task for the current user in the database.
    Expects JSON payload with 'text' and/or 'completed'.
    """
    if not session.get('logged_in'):
        return jsonify({"error": "Unauthorized"}), 401

    user_id = session.get('user_id')
    data = request.get_json()
    db = get_db()
    try:
        # Check if task exists AND belongs to the current user
        task = db.execute('SELECT * FROM tasks WHERE id = ? AND user_id = ?', (task_id, user_id)).fetchone()
        if not task:
            return jsonify({"error": "Task not found or unauthorized"}), 404

        update_fields = []
        update_values = []

        if 'text' in data:
            update_fields.append('text = ?')
            update_values.append(data['text'])
        if 'completed' in data:
            update_fields.append('completed = ?')
            update_values.append(data['completed'])

        if not update_fields:
            return jsonify({"error": "No fields to update"}), 400

        update_query = f"UPDATE tasks SET {', '.join(update_fields)} WHERE id = ? AND user_id = ?"
        update_values.append(task_id)
        update_values.append(user_id) # Ensure update is for the correct user

        db.execute(update_query, tuple(update_values))
        db.commit()

        updated_task = db.execute('SELECT id, text, completed FROM tasks WHERE id = ?', (task_id,)).fetchone()
        return jsonify(dict(updated_task))
    except sqlite3.Error as e:
        db.rollback()
        return jsonify({"error": f"Database error: {e}"}), 500


@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """
    API endpoint to delete a task for the current user from the database.
    """
    if not session.get('logged_in'):
        return jsonify({"error": "Unauthorized"}), 401

    user_id = session.get('user_id')
    db = get_db()
    try:
        # Delete task only if it belongs to the current user
        cursor = db.execute('DELETE FROM tasks WHERE id = ? AND user_id = ?', (task_id, user_id))
        db.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Task not found or unauthorized"}), 404
        return jsonify({"message": "Task deleted successfully"}), 200
    except sqlite3.Error as e:
        db.rollback()
        return jsonify({"error": f"Database error: {e}"}), 500

# Run the Flask application
if __name__ == '__main__':
    # Create the database file if it doesn't exist
    if not os.path.exists(DATABASE):
        open(DATABASE, 'a').close()
        print(f"Created empty database file: {DATABASE}")

    app.run(debug=True)
