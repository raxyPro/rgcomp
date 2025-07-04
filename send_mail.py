import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_mail():
    smtp_server = 'mail.rcpro.in'
    smtp_port = 587
    smtp_username = 'connect@rcpro.in'
    smtp_password = 'HostingMail00$'
    sender_email = 'connect@rcpro.in'
    sender_name = 'rcPro Connect'
    recipient_email = ['rampal3d@gmail.com','rampalxyz@gmail.com']

    # Create the email
    msg = MIMEMultipart('alternative')
    msg['From'] = f'{sender_name} <{sender_email}>'
    msg['To'] = ', '.join(recipient_email)
    msg['Subject'] = 'Hello from Python! (HTML Email)'

    # Plain text and HTML versions
    text = 'This is a test email sent from a Python script!'
    html = """
    <html>
      <body>
        <h2 style="color: #2e6c80;">Hello from <b>Python</b>!</h2>
        <p>This is a <b>test email</b> sent from a <span style="color: green;">Python script</span>!</p>
        <hr>
        <p>Regards,<br><i>rcPro Collab Team</i></p>
      </body>
    </html>
    """

    # Attach both plain and HTML parts
    msg.attach(MIMEText(text, 'plain'))
    msg.attach(MIMEText(html, 'html'))

    # Send the email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(smtp_username, smtp_password)
        for recipient in recipient_email:
            server.sendmail(sender_email, recipient, msg.as_string())
            print(f'Mail sent successfully to {recipient}!')

if __name__ == '__main__':
    print('Starting the mail sender...')
    send_mail()
