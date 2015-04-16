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

class email_sender:

  team_email = "team.struct.by.lightning@gmail.com"

  def _init_(sender_name, sender_email, group_join, recipient_email):
    self.sender_name = sender_name
    self.sender_email = sender_email
    self.recipient_email = recipient_email
    self.group_join = group_join

  def personalize_message(send_name, send_email, join_group, recip_email, email_type):

    if email_type == "invite":
      return "Hello!" + os.linesep + os.linesep + "You have been invited into the Benedictation system.  Benedictation is a video conferencing web application with a smart assistant for your meeting needs.  " + send_name + " invited you to join the chat group " + join_group + ".  Follow this link to join the group:" + os.linesep + os.linesep + "https://benedictation.io" + os.linesep + os.linesep + "Thank you and enjoy!" + os.linesep + os.linesep + "Team Struct by Lightning"


  def send_email(send_name, send_email, join_group, recip_email, email_type):
    # Open a plain text file for reading.  For this example, assume that
    # the text file contains only ASCII characters.

    msg = MIMEMultipart()

    # Create a text/plain message
    text = MIMEText(personalize_message(send_name, send_email, join_group, recip_email, email_type))
    msg.attach(text)

    msg['Subject'] = send_name + ' invited you to join Benedictation'
    msg['From'] = send_email #usually the team email
    msg['To'] = recip_email

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls() # upgrades plain text to secure

    # log in to the server
    server.login("team.struct.by.lightning", yml_dict_email['email']['passwords'])

    # Send the message via our own SMTP server
    server.sendmail(send_email, [recip_email], msg.as_string())
    server.quit()
