# Import smtplib for the actual sending function
import smtplib
from email.mime.base import MIMEBase
import mimetypes
import zipfile
from email import encoders
import yaml

#os
import os

# Import the email modules we'll need
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart


f = open('passwords.yml')
yml_dict_email = yaml.safe_load(f)
f.close()

class email_sender():

  team_email = "team.struct.by.lightning@gmail.com"

  def __init__(self, sender_name, sender_email, group_join, recipient_email, email_type):
    self.sender_name = sender_name
    self.sender_email = sender_email
    self.recipient_email = recipient_email
    self.group_join = group_join
    self.email_type = email_type

  def personalize_message(self, send_name, send_email, join_group, recip_email, email_type):

    if email_type == "invite":
      ret_string = ("Hello! \n \n You have been invited into the"
                    "Benedictation system.  Benedictation is a video conferencing web application"
                    "with a smart assistant for your meeting needs.  " + send_name + " invited "
                    "you to join the chat group " + join_group + ".  Follow this link to join the "
                    "group: \n\n https://benedictation.io \n\n"
                    "Thank you and enjoy! \n\n Team Struct"
                    " by Lightning")
      return ret_string

    return ""


  def send_email(self, send_name, send_email, join_group, recip_email, email_type):
    # Open a plain text file for reading.  For this example, assume that
    # the text file contains only ASCII characters.

    msg = MIMEMultipart()

    # Create a text/plain message
    text = MIMEText(self.personalize_message(send_name, send_email, join_group, recip_email, email_type))
    msg.attach(text)

    msg['Subject'] = send_name + ' invited you to join Benedictation'
    msg['From'] = send_email #usually the team email
    msg['To'] = recip_email

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls() # upgrades plain text to secure

    # log in to the server
    server.login("team.struct.by.lightning", str(yml_dict_email['email']['password']))

    # Send the message via our own SMTP server
    server.sendmail(send_email, [recip_email], msg.as_string())
    server.quit()

if __name__ == "__main__":
  se = email_sender("Kevin Malta", "team.struct.by.lightning@gmail.com", "Scrum", "iamburitto@gmail.com", "invite")
  se.send_email(se.sender_name, se.sender_email, se.recipient_email, se.group_join, se.email_type)

