# Import the dependencies.
import numpy as np
import pandas as pd
import sqlalchemy
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Station = Base.classes.station
measurement = Base.classes.measurement


# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
# Create an app.
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def hello():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )
#Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.
#Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
    prcp_date = session.query(measurement.date, measurement.prcp).all()
    
    session.close()

    all_prcp_date = []
    for prcp, date in prcp_date:
        prcp_dict = {}
        prcp_dict["precipitation"] = prcp
        prcp_dict["date"] = date
        all_prcp_date.append(prcp_dict)

    return jsonify(all_prcp_date)

#Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    active_stations = session.query(Station.station).all()
    
    session.close()
    
    station_list = list(np.ravel(active_stations))
    
    return jsonify(station_list)

#Query the dates and temperature observations of the most-active station for the previous year of data.
#Return a JSON list of temperature observations for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    latest_date = "2017-08-23" - dt.timedelta(days=365)
    most_active= "USC00519281"
    temp_results = session.query(measurement.date, measurement.station, measurement.tobs).filter(measurement.station==most_active).filter(measurement.date >= latest_date).all()
    
    session.close()
    temp_list = list(np.ravel(temp_results))

    return jsonify(temp_list) 

#Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
#For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
#For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.
@app.route("/api/v1.0/start")
def start_date(date):
    
    session = Session(engine)

    start_temp = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).filter(measurement.date>=date).all()
    return jsonify(start_temp)

@app.route("/api/v1.0/<start></end>")
def end_date(start, end):
    
    session = Session(engine)

    end_results = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).filter(measurement.date>=start).filter(measurement.date<=end).all()
    return jsonify(end_results)

if __name__ == '__main__':
    app.run(debug=True)