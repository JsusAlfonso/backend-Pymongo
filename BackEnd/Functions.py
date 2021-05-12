# -*-coding:iso-8859-15-*-
# -*- coding: utf-8 -*-
# -*- coding: 850 -*-
# -*- coding: cp1252 -*-
from flask import Flask, jsonify, request
from pymongo import MongoClient
from pprint import pprint

#python version 2.7.15 - 3
# import globalinfo.Keys as globalkeys
# import globalinfo.Messages as globalMessages

#python version 3.9.5
from .globalinfo import Messages as globalMessages
from .globalinfo import Keys as globalkeys

import json
import sys
import re
import base64
import uuid
	
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from smtplib import SMTP
import os
from os import path
import smtplib
import datetime
from datetime import date, timedelta
import time
import collections
import math
import jwt 
import random
from bson.objectid import ObjectId
from random import SystemRandom

#####################################################################
#		Conexion a la base de datos									#
#####################################################################
def connectDB():
    if not globalkeys.dbconn:
	    globalkeys.dbconn = MongoClient(globalkeys.strConnection).runners #nombre de la base de datos
    return globalkeys.dbconn

#####################################################################
#		Busca el usuario en la base de datos Api tipo GET			#
#####################################################################
def fnUserSearch(strEmail,strPassword):
	try:
		db = connectDB()
		strEmail = strEmail.lower()
		strSearchEmail = db.clUser.find({'strEmail':strEmail})
		strSearchEmailAndPass = db.clUser.find({'strEmail':strEmail, 'strPassword':strPassword})
		if	strSearchEmailAndPass.count() != 0:

			for userInfo in strSearchEmailAndPass:
				
				if userInfo.has_key('strToken'):
					strTokenTime = fnValidateTokenAge(userInfo['strToken'])

					if strTokenTime != '0':
						strToken = {'token':userInfo['strToken']}
					
					else:
						userId = userInfo['_id']
						strToken = fnCreateSession(strEmail, userId)
						db.clUser.update({'_id':ObjectId(userId)},{'$set':{'strToken':strToken['token']}})

				else:
					userId = userInfo['_id']
					strToken = fnCreateSession(strEmail, userId)
					db.clUser.update({'_id':ObjectId(userId)},{'$set':{'strToken':strToken['token']}})

			i = {
				'intResp':'200',
				'strMessage':'Access',
				'strToken':strToken['token']
			}
			return i

		elif strSearchEmail.count() != 0:
			i = {
				'intResp':'201',
				'strMessage':'Incorrect password'
			}
			return i

		else:
			i = {
				'intResp':'202',
				'strMessage':'user not found'
			}
			return i
	except excepcion as e:
		return globalMessages.err500

#####################################################################
#		Inserta un nuevo usuario Api tipo PUT   					#
#####################################################################
def fnRegisterUser(strName,strEmail,doubWeight,doubHeight,doubTotal,strPassword):
	try:

		db = connectDB()
		strEmail = strEmail.lower()
		strSearch = db.clUser.find({'strEmail':strEmail})
		if strSearch.count() != 0:
			i = {
				'intResp':'100',
				'strMessage':'This user was already registered'
			}
			return jsonify(i)

		db.clUser.insert({'strName':strName,'strEmail':strEmail,'strPassword':strPassword, 'doubHeight':float(doubHeight), 'arrIMC':[{'dteIMC':datetime.datetime.now(),'doubWeight':float(doubWeight), 'doubTotal':float(doubTotal)}]})
		i = {
			'intResp':'200',
			'strMessage':'Usuer '+strName+' registered correctly'
		}
		return jsonify(i)
		
	except excepcion as e:
		return globalMessages.err500

#####################################################################
#		Crea sesion token en el server			   					#
#####################################################################
def fnCreateSession(strEmail,userID):
	try:
		today = datetime.datetime.today()
		tomorrow = today + datetime.timedelta(days=1)
		today = time.mktime(today.timetuple())
		tomorrow = time.mktime(tomorrow.timetuple())
		jsnInformation = {'strEmail': str(strEmail),'strID':str(userID),'iat': today,'exp': tomorrow}
		encoded = jwt.encode(jsnInformation, 'secret', algorithm='HS256')
		response = {'intResp':'200','strValue':'Session created','token': encoded,'strID':userID}
		return response
	
	except Exception as e:
		response = {'intResp':'0','strValue':'Error: Fails to create the user'}
		return response

#####################################################################
#		Valida la caducida del token			   					#
#####################################################################
def fnValidateTokenAge(strToken):
	db = connectDB()
	try:
		#Busca el token en la base de datos y lo valida
		TokenExists = db.clUser.find_one({'strToken': strToken})
		if TokenExists:
			decoded = jwt.decode(strToken, 'secret', algorithms=['HS256'])
			IDUser = decoded['strID']
			expToken = decoded["exp"]
			iatToken = decoded["iat"]
			today = datetime.datetime.today()
			today = time.mktime(today.timetuple())
			#pregunta si es la fecha de hoy menor que la de fin del token 
			if today <= expToken:
				return IDUser
			else:
				return '0'
		else:
			return '0'
	except Exception as e:
		return '0'

#####################################################################
#		Devuelve la informacion del usuario		   					#
#####################################################################
def fnUserInfo(strToken):
	db = connectDB()
	try:
		strTokenAge = fnValidateTokenAge(strToken)
		if strTokenAge != '0':
			userInfo = db.clUser.find({'strToken':strToken})
			for info in userInfo:
				i = {
					'intResp':'200',
					'strName': info['strName'],
					'strEmail':info['strEmail'],
					'doubHeight': info['doubHeight'],
					'arrIMC': info['arrIMC']
				}
			return i
		else:
			response = {'intResp':'220','strMessage':'Expired session'}
			return response
	except excepcion as e:
		return globalMessages.err500

#####################################################################
#		Actualiza la informacion del usuario		   				#
#####################################################################
def fnUpdateInfoUser(strUserName, strUserPwd, strToken):
	db = connectDB()
	try:
		strTokenAge = fnValidateTokenAge(strToken)
		if strTokenAge == '0':
			response = {'intResp':'220','strMessage':'Expired session'}
			return response

		if strUserName == '':
			i = {'intResp':'265', 'strMessage':'User Name Empty'}
		if strUserPwd != '':
			db.clUser.update({'strToken':strToken},{'$set':{'strName':strUserName, 'strPassword':strUserPwd}})
			i = {'intResp':'200','strMessage':'user Modify'}
			return i
		else:
			db.clUser.update({'strToken':strToken},{'$set':{'strName':strUserName}})
			i = {'intResp':'200','strMessage':'user Modify'}
			return i
	except excepcion as e:
		return globalMessages.err500

#####################################################################
#		Borra toda la informacion del usuario		   				#
#####################################################################
def fnDeleteUser(strToken):
	try:
		db = connectDB()
		strTokenAge = fnValidateTokenAge(strToken)
		if strTokenAge == '0':
			response = {'intResp':'220','strMessage':'Expired session'}
			return response
		db.clUser.remove({"strToken" : strToken})
		i = {'intResp':'200', 'strMessage':'User Deleted'}
		return i
	except excepcion as e:
		return globalMessages.err500

#####################################################################
#		Inserta el IMC en el array del usuario		   				#
#####################################################################
def fnUpdateUserIMC(doubWeight, strToken):
	try:
		db = connectDB()
		strTokenAge = fnValidateTokenAge(strToken)
		if strTokenAge == '0':
			response = {'intResp':'220','strMessage':'Expired session'}
			return response
		userInfo = db.clUser.find({'strToken':strToken})
		for info in userInfo:
			arrIMC = info['arrIMC']
			doubHeight = float(info['doubHeight']) * float(info['doubHeight'])
		doubTotal = float(doubWeight) / doubHeight
		arrIMC.append({'dteIMC':datetime.datetime.now(),'doubWeight':float(doubWeight), 'doubTotal':float(doubTotal)})
		db.clUser.update({'strToken':strToken},{'$set':{'arrIMC':arrIMC}})
		i = {'intResp':'200', 'strMessage':'IMC inserted correctly', 'arrIMC':arrIMC}
		return i
	except excepcion as e:
		return globalMessages.err500

#####################################################################
#		Devuelve la informacion del usuario	buscado					#
#####################################################################
def fnOtherUserInfo(strEmail):
	db = connectDB()
	try:
		if strEmail != '':
			userInfo = db.clUser.find({'strEmail':strEmail})
			if userInfo.count() == 0:
				response = {'intResp':'222','strMessage':'User not found'}
				return response
			for info in userInfo:
				i = {
					'intResp':'200',
					'strName': info['strName'],
					'strEmail':info['strEmail'],
					'doubHeight': info['doubHeight'],
					'arrIMC': info['arrIMC']
				}
			return i
		else:
			response = {'intResp':'202', 'strMessage':'user not found'}
			return response
	except excepcion as e:
		return globalMessages.err500
