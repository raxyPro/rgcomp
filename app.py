from flask import Flask, request, render_template_string
from flask_mail import Mail, Message
import datetime
import requests

app = Flask(__name__)

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'mail.rcpro.in'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'connect@rcpro.in'
app.config['MAIL_PASSWORD'] = 'HostingMail00$'
app.config['MAIL_DEFAULT_SENDER'] = ('rcPro Connect', 'connect@rcpro.in')

mail = Mail(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    def get_random_quote():
        try:
            response = requests.get("https://api.quotable.io/random", timeout=5)
            if response.status_code == 200:
                return response.json().get("content", "No quote found.")
            else:
                return "No quote found."
        except Exception:
            return "No quote found."

    if request.method == 'POST':
        recipient = request.form['email']
        subject = request.form['subject']
        #body = request.form['body']
        body = f"""
<html>
    <body>
        <h2 style="color:#2E86C1;">You're Invited to Join rcPro Connect!</h2>
        <p>Dear User,</p>
        <p>
            We are excited to invite you to join <b>rcPro Connect</b> – your gateway to a vibrant community of professionals and enthusiasts.
        </p>
        <p>
            <a href="https://rcpro.in/connect" style="background-color:#2E86C1;color:#fff;padding:10px 20px;text-decoration:none;border-radius:5px;">Join Now</a>
        </p>
        <p>
            Connect, collaborate, and grow with us.<br>
            <br>
            Best regards,<br>
            The rcPro Team
        </p>
        <hr>
        <small>If you did not request this invitation, please ignore this email.</small>
    </body>
</html>
"""
        msg = Message(subject, recipients=[recipient])
        msg.html = body
        msg = Message(subject, recipients=[recipient], body=body)
        mail.send(msg)
        return 'Email sent!'
    
    # Defaults
    default_email = "rampalxyz@gmail.com"
    default_subject = f"test {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    default_body = get_random_quote()

    return render_template_string('''
        <form method="post">
            To: <input type="email" name="email" value="{{email}}"><br>
            Subject: <input type="text" name="subject" value="{{subject}}"><br>
            Body: <textarea name="body">{{body}}</textarea><br>
            <input type="submit" value="Send">
        </form>
    ''', email=default_email, subject=default_subject, body=default_body)
if __name__ == '__main__':
    app.run(debug=True)