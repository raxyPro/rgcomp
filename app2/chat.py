# chat.py
import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template_string, request
from flask_socketio import SocketIO, emit
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# In-memory storage for messages (not persistent)
messages = []

# HTML as a variable (rendered inline)
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>WebSocket Chat</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.0/socket.io.min.js"></script>
    <style>
        body { font-family: sans-serif; margin: 20px; background: #f4f4f4; }
        #chat { height: 300px; overflow-y: scroll; padding: 10px; border: 1px solid #ccc; background: white; }
        #chat div { margin-bottom: 10px; }
    </style>
</head>
<body>
    <h2>WebSocket Chat</h2>
    <div id="chat"></div>
    <input type="text" id="username" placeholder="Username" style="width: 150px;">
    <input type="text" id="message" placeholder="Type a message..." style="width: 300px;">
    <button onclick="sendMessage()">Send</button>

    <script>
        const socket = io();

        socket.on('connect', () => {
            console.log('Connected to WebSocket server.');
        });

        socket.on('new_message', data => {
            const chat = document.getElementById('chat');
            const div = document.createElement('div');
            div.innerHTML = `<strong>${data.username}:</strong> ${data.message}`;
            chat.appendChild(div);
            chat.scrollTop = chat.scrollHeight;
        });

        function sendMessage() {
            const username = document.getElementById('username').value.trim();
            const message = document.getElementById('message').value.trim();
            if (!username || !message) return;
            socket.emit('send_message', { username, message });
            document.getElementById('message').value = '';
        }

        // Load initial messages
        fetch('/messages')
            .then(res => res.json())
            .then(data => {
                const chat = document.getElementById('chat');
                data.forEach(msg => {
                    const div = document.createElement('div');
                    div.innerHTML = `<strong>${msg.username}:</strong> ${msg.message}`;
                    chat.appendChild(div);
                });
                chat.scrollTop = chat.scrollHeight;
            });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(html_template)

@app.route('/messages')
def get_messages():
    return messages

@socketio.on('send_message')
def handle_message(data):
    data['timestamp'] = datetime.utcnow().isoformat()
    messages.append(data)
    emit('new_message', data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='127.0.0.1', port=5200)

