import smtplib
from email.mime.text import MIMEText
from email.header import Header

sender = 'tom.zhou@calix'
receiver = 'tom.zhou@calix.com'
subject = 'Bug reproduced yeah!'

username = 'zhoumg@gmail.com'
password = 'thtfopac@123'
msg = MIMEText('Bug is found', 'text', 'utf-8')
msg['Subject'] = Header(subject, 'utf-8')

server = 'smtp.gmail.com'

smtp = smtplib.SMTP(server, 587)
smtp.set_debuglevel(5)
smtp.starttls()
smtp.login(username, password)

smtp.sendmail(sender, receiver, msg.as_string())
smtp.quit()