#!/usr/bin/python
# -*- coding:Utf-8 -*-

import urllib, urllib2
import libxml2

class EnvoiSms(object):
	'''
		From http://api.orange.com/fr/api/sms-api/documentation
	'''

	url_api = 'http://run.orangeapi.com/sms/sendSMS.xml?'
	params = {'id' : '', #clé api
			'from' : '38100', #numéro d'envoi
			'to' : '', #numéro de portable
			'content' : '', #contenu
			'long_text' : '1', #autoriser fragmentation du sms
			'max_sms' : '10', #nombre de fragments max
			'ack' : '0',

		}

	def __init__(self,api_key):
		self.params['id'] = api_key


	def envoi(self,numero,message):
		self.params['to'] = numero
		self.params['content'] = message
		url = self.url_api + urllib.urlencode(self.params)
		r = urllib2.urlopen(url)
		doc = libxml2.parseDoc(r.read())
		ctxt = doc.xpathNewContext()
		res = ctxt.xpathEval("/response/status/status_code/text()")
		return res[0]

