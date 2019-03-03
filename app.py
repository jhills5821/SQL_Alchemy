import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Flask Setup
app = Flask(__name__)

# Flask Routes
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of precipitation data"""
    # Query all 
    results = session.query(Measurement.date,Measurement.prcp).all()

    prcp_data = []
    for date in results:
        prcp_dict = {}
        prcp_dict[date.date] = date.prcp
        prcp_data.append(prcp_dict)

    return jsonify(prcp_data)


@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations"""
    # Query all stations
    results = session.query(Measurement.station).group_by(Measurement.station).all()

    # Create a list from the row data and append to a list of stations
    stations = list(np.ravel(results))

    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def temperature():
    """Return a list of temperature data"""
    # Query all tobs
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = str(np.ravel(last_date))

    query_date = dt.datetime.strptime(last_date,"['%Y-%m-%d']")

    year_ago = query_date - dt.timedelta(days=365)

    # Perform a query to retrieve the date and tobs scores
    sel = [Measurement.date, Measurement.tobs]
    results = session.query(*sel).filter(Measurement.date >= year_ago ).all()

    tobs_data = []
    for date in results:
        tobs_dict = {}
        tobs_dict[date.date] = date.tobs
        tobs_data.append(tobs_dict)

    return jsonify(tobs_data)

@app.route("/api/v1.0/<start>")
def calc_temp_start(start):
    """Return a list of min, max and avg temperature data without an end date"""

    # Perform a query to retrieve the temp info without end date
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    results = session.query(*sel).filter(Measurement.date >= start).all()
    results = list(np.ravel(results))

    tobs_info_start = []
    tobs_info_start_dict = {}
    tobs_info_start_dict['min'] = results[0]
    tobs_info_start_dict['avg'] = results[1]
    tobs_info_start_dict['max'] = results[2]
    tobs_info_start.append(tobs_info_start_dict)

    return jsonify(tobs_info_start)

@app.route("/api/v1.0/<start>/<end>")
def calc_temp(start,end):
    """Return a list of min, max and avg temperature data"""

    # Perform a query to retrieve the temp info with both start and end date
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    results = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    results = list(np.ravel(results))

    tobs_info = []
    tobs_info_dict = {}
    tobs_info_dict['min'] = results[0]
    tobs_info_dict['avg'] = results[1]
    tobs_info_dict['max'] = results[2]
    tobs_info.append(tobs_info_dict)

    return jsonify(tobs_info)

if __name__ == '__main__':
    app.run(debug=True)