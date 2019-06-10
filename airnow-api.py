import config   #config for api keys
import requests #for api requests
import json     #for json funcs


from flask import Flask, jsonify, request, redirect, url_for
from flask_cors import CORS

import datetime, operator       # time stamps on the GET and PUSH req.
from datetime import datetime   # get date/current time 

import flask_sqlalchemy as sqlalchemy    # entire sqlalchemy library
from passlib.hash import pbkdf2_sha256   # for hashing user info.
from sqlalchemy import inspect, Table, Column, Integer, ForeignKey


'''
Zane Partain
  AirNow.gov api program
  Open-Weather-Map api program
5/24/2019
'''

#Database configuration#
app = Flask(__name__) 
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlalchemy-demo.db'
db = sqlalchemy.SQLAlchemy(app)
base_url = '/api/'

AIR_KEY = config.AIR_KEY          #my air api key
WEATHER_KEY = config.WEATHER_KEY  #my weather api key

#data to be sent for GET request
data = {
    "zipcode" : "",
    "distance" : "",
    "API_KEY": AIR_KEY
}


@app.route(base_url + 'currentAQI',methods=["GET"])
def getAQI():
  #get query parameters
  data["zipcode"] = request.args.get('zipcode')
  data["distance"] = request.args.get('distance')
  
  #format url string
  # need to have zipcode, distance, api_key
  url = """http://www.airnowapi.org/aq/observation/zipCode/current/
        ?format=application/json&zipCode={}&distance={}&API_KEY={}""".format(data["zipcode"],data["distance"],AIR_KEY)

  response = requests.get(url)  #make api request
  if response.status_code == 200 and len(response.text) > 2:
    #load resulting string into json
    packed_json = json.loads(response.text)
    target_json = findHighestPollutant(packed_json)

    return jsonify({"status": 1, "response":[target_json]})
  else:
    return jsonify({"status":0, "response": ""})
    

@app.route(base_url + 'currentWeather', methods=["GET"])
def getWeather():
  #get query parameters
  zipcode = request.args.get('zipcode')
  country = ',us'

  #base weather api url
  url_w_base = 'http://api.openweathermap.org/data/2.5/weather?'

  #complete url for open weather map zicode
  #api GET requests
  complete_url = url_w_base + '&zip=' + zipcode + country + '&APPID=' + WEATHER_KEY + '&units=imperial'

  response = requests.get(complete_url)  #make GET request

  res = response.json() #turn response to json

  #ensure that the response was successful
  if(res['cod'] != '404'):
    return jsonify({"status": 1, "data":OWM_to_obj(res)})
  else:
    return jsonify({"status":0, "response": ""})


#Turn OWM response data into an object 
def OWM_to_obj(w_data):
  date_time = datetime.fromtimestamp(w_data['dt']).strftime('%c')

  owm = {
    "main": w_data['main'],
    "weather" : w_data['weather'][0],
    "wind": w_data['wind'],
    "name": w_data['name'],
    "dt" : date_time,
  }

  return owm


#find the JSON data that only has ParameterName='PM2.5'
def findHighestPollutant(packed_json):
  count = 0
  currentAQI = 0
  target_json = {}
  for entry in packed_json:
    if entry['AQI'] > currentAQI:
      currentAQI = entry['AQI']
      target_json = packed_json[count]
    count += 1

  return target_json


'''
MAIN
'''
def main():
  #db.create_all()  #for local hosting
  app.run()

if __name__ == '__main__':
  main()