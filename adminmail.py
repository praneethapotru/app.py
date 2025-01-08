import smtplib
from smtplib import SMTP
from email.message import EmailMessage
def adminsendmail(to,subject,body):
    server=smtplib.SMTP_SSL('smtp.gmail.com',465)
    server.login('praneethapotru128@gmail.com','qugx gcgl uegz kxca')
    msg=EmailMessage()
    msg['From']='praneethapotru128@gmail.com'
    msg['Subject']=subject
    msg['To']=to
    msg.set_content(body)
    server.send_message(msg)
    server.quit()
