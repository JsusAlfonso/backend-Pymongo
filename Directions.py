#!/usr/bin/env python
# -*- coding: 850 -*-
# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-
#direcciones de las funciones
from flask_cors import CORS,cross_origin 
import BackEnd.Functions as callMethod

from flask import Flask, jsonify, request, url_for
import datetime

import json
import sys

import requests
import os
from werkzeug.utils import secure_filename
from decimal import *
import base64

app = Flask(__name__)
CORS(app)
#Inicio de codigo

###################################################################
#Api de prueba ####################################################
###################################################################
@app.route('/api/fnExample/<strName>/<strEmail>/<doubWeight>/<doubHeight>/<doubTotal>', methods=['GET'])
def exampleMessage(strName,strEmail,doubWeight,doubHeight,doubTotal):
	try:
		bolResult = callMethod.fnExampleMessage(strName,strEmail,doubWeight,doubHeight,doubTotal)
		return bolResult
	except Exception as e:
		respuesta = {'intResp':'0'}
		return jsonify(respuesta)


###################################################################
# Api para registrar un nuevo usuario #############################
###################################################################
@app.route('/api/registerUser', methods=['POST'])
def postRegisterUser():
	try:
		strName = request.json["Name"]
		strEmail = request.json["Email"]
		doubWeight = request.json["Weight"]
		doubHeight = request.json["Height"]
		doubTotal = request.json["Total"]
		strPassword = request.json["strPassword"]

		bolResult = callMethod.fnRegisterUser(strName,strEmail,doubWeight,doubHeight,doubTotal,strPassword)
		return bolResult
	except Exception as e:
		respuesta = {'intResp':'0'}
		return jsonify(respuesta)

###################################################################
#Api para buscar un usuario #######################################
###################################################################
@app.route('/api/fnUser/<strEmail>/<strPassword>', methods=['GET'])
def userSearch(strEmail,strPassword):
	try:
		strResult = callMethod.fnUserSearch(strEmail,strPassword)
		return jsonify(strResult)

	except Exception as e:
		print(e)
		respuesta = {'intResp':'0'}
		return jsonify(respuesta)


###################################################################
#Api Que trae la informacion del usuario###########################
###################################################################
@app.route('/api/fnUserInfo/<strToken>', methods=['GET'])
def getUserInfo(strToken):
	try:
		arrResult = callMethod.fnUserInfo(strToken)
		return jsonify(arrResult)

	except Exception as e:
		respuesta = {'intResp':'0'}
		return jsonify(respuesta)


###################################################################
# Api para registrar un nuevo usuario #############################
###################################################################
@app.route('/api/fnUpdateUserInfo', methods=['PUT'])
def putUpdateUserInfo():
	try:
		strUserName = request.json["strUserName"]
		strUserPwd = request.json["strUserPwd"]
		strToken = request.json["strToken"]

		strResult = callMethod.fnUpdateInfoUser(strUserName,strUserPwd,strToken)
		return jsonify(strResult)
	except Exception as e:
		respuesta = {'intResp':'0',
					 'strMessage':'Erro in the api'}
		return jsonify(respuesta)
		
###################################################################
# Api para Borrar un usuario 		  #############################
###################################################################
@app.route('/api/fnDeleteUser', methods=['DELETE'])
def deleteUserInfo():
	try:
		strToken = request.json["strToken"]

		strResult = callMethod.fnDeleteUser(strToken)
		return jsonify(strResult)
	except Exception as e:
		respuesta = {'intResp':'0',
					 'strMessage':'Erro in the api'}
		return jsonify(respuesta)

###################################################################
# Api para insertar el nuevo IMC	  #############################
###################################################################
@app.route('/api/fnUpdateIMC', methods=['PUT'])
def putUpdateIMC():
	try:
		doubWeight = request.json["doubWeight"]
		strToken = request.json["strToken"]

		strResult = callMethod.fnUpdateUserIMC(doubWeight, strToken)
		return jsonify(strResult)
	except Exception as e:
		respuesta = {'intResp':'0',
					 'strMessage':'Erro in the api'}
		return jsonify(respuesta)

###################################################################
#Api Que trae la informacion de otro usuario#######################
###################################################################
@app.route('/api/fnOtherUserInfo/<strEmail>', methods=['GET'])
def getOtherUserInfo(strEmail):
	try:
		arrResult = callMethod.fnOtherUserInfo(strEmail)
		return jsonify(arrResult)

	except Exception as e:
		respuesta = {'intResp':'0'}
		return jsonify(respuesta)

#Final del codigo
if __name__ == '__main__':
	app.run(host="0.0.0.0",port=5050,debug=True,threaded=True)