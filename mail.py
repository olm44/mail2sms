#!/usr/bin/python
# -*- coding:Utf-8 -*-

import imaplib, email
from getpass import getpass
import urllib, urllib2

from EnvoiSms import *

import sys, time
from Daemon import Daemon
from TaskThread import TaskThread


class MailThread(TaskThread):
    """Vérifie les mails toutes les N minutes"""
    
    def __init__(self, mail, api, numero, folder):
        TaskThread.__init__(self)
        self.mail = mail
        self.api = api
        self.folder = folder
        self.numero = numero    

    def get_first_text_block(self, email_message_instance):
        maintype = email_message_instance.get_content_maintype()
        if maintype == 'multipart':
            for part in email_message_instance.get_payload():
                if part.get_content_maintype() == 'text':
                    return part.get_payload()
        elif maintype == 'text':
            return email_message_instance.get_payload()
    
    def task(self):
        for f in self.folder:
            self.mail.select(f) # connect to inbox.
            result, data = self.mail.search(None, 'UnSeen') #UnSeen : Unread mails
            ids = data[0] # data is a list.
            id_list = ids.split() # ids is a space separated string
            for new_mail in id_list:
                #latest_email_id = id_list[-1] # get the latest
                result, data = self.mail.fetch(new_mail, "(RFC822)") # fetch the email body (RFC822) for the given ID
                raw_email = data[0][1] # here's the body, which is raw text of the whole email
                # including headers and alternate payloads
                email_message = email.message_from_string(raw_email)
                content_sms = { 'From' : email.utils.parseaddr(email_message['From']),
                'Subject' :  email_message['Subject'],
                'Content' : self.get_first_text_block(email_message)}
                #self.api.envoi(self.numero, "Nouveau mail de " + content_sms['From'][0] + " : " + content_sms['Subject'])
                print "mail !"


class MailInstance(object):

    def __init__(self, server, login, password, time, api, numero, *folder):
        self.server = server
        self.login = login
        self.password = password
        self.time = time
        self.folder=[]
        if not folder : self.folder.append("inbox")
        for f in folder:
            self.folder.append(f)
        self.api = api
        self.numero = numero


    def connect(self):
        mail = imaplib.IMAP4_SSL(self.server)
        mail.login(self.login, self.password)
        mail.list()
        # Out: list of "folders" aka labels in gmail.
        
        self.checkMail = MailThread(mail, self.api, self.numero, self.folder)
        self.checkMail.setInterval(self.time)
        self.checkMail.daemon = True
        self.checkMail.start()

    def stop():
        self.checkMail.shutdown()

'''
def main():
    api = EnvoiSms('api_key')
    gmail = MailInstance('imap.gmail.com','login', "password", 300, api, "000000000", "Label1", "Label2")
    try:
        gmail.connect()        
        while True: pass
    except (KeyboardInterrupt, SystemExit):
        print '\n! Received keyboard interrupt, quitting threads.\n'
'''

class Mail2Sms(Daemon):
    def run(self):
        api = EnvoiSms('api_key')
        gmail = MailInstance('imap.gmail.com','login', "password", 300, api, "000000000", "Label1", "Label2")
        gmail.connect()  
        while True:
            time.sleep(1)
 
if __name__ == "__main__":
    daemon = Mail2Sms('/tmp/mail2sms.pid',stderr='/tmp/mail2sms.err.log',stdout='/tmp/mail2sms.out.log')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)