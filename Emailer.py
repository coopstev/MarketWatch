import smtplib
#from email.mime.text import MIMEText
from email.message import EmailMessage

## put SMTP username, password, and email_from here
EMAIL_SUBJECT = "Notification from MarketWatch"

class Emailer:
    def __init__(self, recipients=[]):
        self.recipients = recipients

        emailInfo = open(f"./secrets/mailInfo.txt", 'r')
        self._SMTP_SERVER = emailInfo.readline().split()[1]
        self._SMTP_PORT = int(emailInfo.readline().split()[1])
        self._SENDER = emailInfo.readline().split()[1]
        emailInfo.close()
    
    def __del__(self):
        try:
            self.logout()
        except:
            pass

    def login(self):
        self.mail = smtplib.SMTP(self._SMTP_SERVER, self._SMTP_PORT)
        self.mail.starttls()
        self.mail.login(self._SENDER, self._getAppPassword())

    def logout(self):
        self.mail.quit()

    def _getAppPassword(self):
        appPasswordFile = open(f"./secrets/GmailAppPassword.txt", 'r')
        appPassword = appPasswordFile.readline()
        appPasswordFile.close()
        return appPassword

    def readTxtFile(self, path=''):
        file = open(path, 'r')
        content = file.read()
        file.close()
        return content
    
    def send_email(self, msgFilePath=''):
        try:
            content = self.readTxtFile(msgFilePath)
            msg = EmailMessage()
            #msg = MIMEText(msg_txt)
            msg['Subject'] = EMAIL_SUBJECT
            msg['From'] = self._SENDER
            msg['To'] = self.recipients
            msg.set_content(content)

            self.login()
            self.mail.send_message(msg, self._SENDER, self.recipients)
            #self.mail.sendmail(self._SENDER, recipients, msg.as_string())
            self.logout()
        except Exception as e:
            print(f"Emailer Exception: {e}")
            return False
        return True

    def refresh_connection(self):
        try:
            self.logout()
        except:
            pass
        self.login()
    