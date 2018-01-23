#Copyright Alexandria Books All Rights Reserved

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

class EmailDriver(object):

    def __init__(self, host, port, email, password):

        self.host = host
        self.port = port
        self.email = email
        self.password = password
        self.set_up()


    def set_up(self):

        self.server = smtplib.SMTP(self.host, self.port)
        self.server.starttls()
        self.server.login(self.email, self.password)


    def send_message(self, message, subject, address):

        msg = MIMEMultipart()
        msg['From'] = self.email
        msg['To'] = address
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))
        self.server.send_message(msg)

