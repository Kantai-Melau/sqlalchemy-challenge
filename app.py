# Import Dependencies
from flask import Flask, jsonify
import matplotlib.pyplot as plt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

import numpy as np
import datetime as dt

engine = engine = create_engine("sqlite:///Resources/hawaii.sqlite")
conn = engine.connect()
Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

# Create an app
app = Flask(__name__)

# Define static routes
@app.route("/")
def Homepage():
    return (
        f"Welcome to the Hawaii Climate API! <br><br>"
        f"These are the available routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    prcp = session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date.desc()).all()
    session.close()

    precipitation = []
    for p in prcp:
        prcp_dict = {}
        prcp_dict["Date"] = p[0]
        prcp_dict["Precipitation"] = p[1]
        precipitation.append(prcp_dict)

    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    stations_data = session.query(Station.station, Station.name).all()
    session.close()

    stations = []
    for station in stations_data:
        station_dict = {}
        station_dict["Station"] = station[0]
        station_dict["Name"] = station[1]
        stations.append(station_dict)

    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)
    most_active_station = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count(Measurement.date).desc()).first()[0]
    
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    ldate = dt.datetime.strptime(latest_date, '%Y-%m-%d')
    query_date = dt.date(ldate.year -1, ldate.month, ldate.day)
    tad = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active_station).filter(Measurement.date >= query_date).all()
    session.close()
    
    temps = []
    for t in tad:
        temp_dict = {}
        temp_dict["Date"] = t[0]
        temp_dict["Tobs"] = t[1]
        temps.append(temp_dict)

        return jsonify(temps)

@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)
    start_temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()

    temp_data = []
    for s in start_temps:
        tempd = {}
        tempd["Min"] = s[0]
        tempd["Avg"] = s[1]
        tempd["Max"] = s[2]
        temp_data.append(tempd)

        return jsonify(temp_data)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    session = Session(engine)
    query_result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start). filter(Measurement.date <= end).all()

    results = []
    for result in query_result:
        r_query = {}
        r_query["Min"] = result[0]
        r_query["Avg"] = result[1]
        r_query["Max"] = result[2]
        results.append(r_query)

        return jsonify(results)

session.close()
if __name__ == "__main__":
    app.run(debug=True)




        