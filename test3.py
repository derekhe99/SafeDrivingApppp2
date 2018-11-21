# -*- coding: utf-8 -*-
"""
Created on Wed Nov 21 01:39:06 2018

@author: iancp
"""

import pandas as pd
from sklearn.cluster import KMeans
import math
from flask import Flask, request, jsonify
from flask_restful import Resource, Api

oseventeen=pd.read_csv('Texas location crash data 2017.csv',skiprows=[1])
osixteen=pd.read_csv('Texas location crash data 2016.csv',skiprows=[1])
ofifteen = pd.read_csv('Texas location crash data 2015.csv',skiprows=[1])
ofourteen = pd.read_csv('Texas location crash data 2014.csv',skiprows=[1])
othirteen = pd.read_csv('Texas location crash data 2013.csv',skiprows=[1])
otwelve = pd.read_csv('Texas location crash data 2012.csv',skiprows=[1])
oeleven = pd.read_csv('Texas location crash data 2011.csv',skiprows=[1])
oten = pd.read_csv('Texas location crash data 2010.csv',skiprows=[1])
ofive = pd.read_csv('Texas location crash data 2005.csv',skiprows=[1])

def createmasterdata(firstNewData,secondNewData):
    mastertexas=pd.concat([firstNewData,secondNewData])
    return mastertexas

mastertexasDF1 = createmasterdata(createmasterdata(createmasterdata(oten,osixteen),oeleven),otwelve)
mastertexasDF2 = createmasterdata(createmasterdata(createmasterdata(oseventeen,othirteen),ofourteen),ofifteen)
mastertexasDF=createmasterdata(mastertexasDF1,mastertexasDF2)

earth_radius = 3960.0
degrees_to_radians = math.pi/180.0
radians_to_degrees = 180.0/math.pi

def change_in_latitude(miles):
    return (miles/earth_radius)*radians_to_degrees

def change_in_longitude(latitude, miles):
    # Find the radius of a circle around the earth at given latitude.
    r = earth_radius*math.cos(latitude*degrees_to_radians)
    return (miles/r)*radians_to_degrees

def location(x,y):
    latmax = x + (change_in_latitude(34));
    latmin = x - (change_in_latitude(34));
    lonmax = y + (change_in_longitude(x,34))
    lonmin = y - (change_in_longitude(x,34))
    
    inputdata = pd.DataFrame([])
    inputdata= mastertexasDF[(mastertexasDF['latitude']>latmin)&(mastertexasDF['latitude']<latmax)&(mastertexasDF['longitude']>lonmin)&(mastertexasDF['longitude']<lonmax)]

    #return masterdata
    return inputdata

def datascale(original):
    return original.iloc[:,[4,8]]

def KMeansData(inputdataset):
    samplekmeans=KMeans(n_clusters=10)
    if len(inputdataset.index) == 0:
        return None
    samplekmeans.fit(inputdataset)
    results=samplekmeans.cluster_centers_
    return results

app = Flask(__name__)
api = Api(app)

class Hotspots(Resource):
    def get(self, lat, lon):
        lat = float(lat)
        lon = float(lon)
        hotspots = KMeansData(datascale(location(lat, lon)))
        if hotspots is None:
            return 400
        hotspots = hotspots.tolist()
        hotspotdict = jsonify({"points":hotspots})
        hotspotdict.status_code = 200
        return hotspotdict

api.add_resource(Hotspots, "/hotspots/<string:lat>/<string:lon>")
app.run(debug=True)