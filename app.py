from flask import Flask, jsonify
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
base = automap_base()
# reflect the tables
base.prepare(engine, reflect=True)

keys = base.classes.keys()

# Save reference to the table
Station = base.classes.station
Measurement = base.classes.measurement

# Create Session
# session = Session(engine)

# Flask Setup
app = Flask(__name__)

@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (
            f"Available Routes:<br/>"
            f"/api/v1.0/precipitation<br/>"
            f"/api/v1.0/stations<br/>"
            f"/api/v1.0/tobs<br/>"
            f"/api/v1.0/<start><br/>"
            f"/api/v1.0/<start>/<end>"
    ) 

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    last_twelve_months = dt.datetime(2017, 8, 23) - dt.timedelta(days=365)
    date_prcp=session.query(Measurement.date,Measurement.prcp).\
                       filter(Measurement.date >= last_twelve_months).\
                        order_by(Measurement.date).all()
    session.close()

    all_data_prcp = []
    for date, prcp in date_prcp:
        Measurement_dict = {}
        Measurement_dict["date"] = date
        Measurement_dict["prcp"] = prcp
        all_data_prcp.append(Measurement_dict)

    return jsonify(all_data_prcp)

@app.route("/api/v1.0/stations")
def stations():

    session = Session(engine)

    all_stations = session.query(Station.name).all()

    all_stations = list(np.ravel(all_stations))
    session.close()
    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    print("Server received request for 'TOBS' page...")
    session = Session(engine)
    last_12_months = dt.datetime(2017, 8, 23) - dt.timedelta(days=365)
    date_temp=session.query(Measurement.date,Measurement.tobs).\
                       filter(Measurement.date >= last_12_months).\
                        filter(Measurement.station == "USC00519281").\
                        order_by(Measurement.date).all()

    session.close()

    all_temps = []
    for date, tobs in date_temp:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["tobs"] = tobs
        all_temps.append(temp_dict)

    return jsonify(all_temps)

@app.route("/api/v1.0/<start>")
def max_temp_start(start):

    session = Session(engine)

    start_date = start
    stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date > start_date).all()

    session.close()

    start_temps = []
    for temp_min, temp_avg, temp_max in stats:
        temp_s_dict = {}
        temp_s_dict["tmin"] = temp_min
        temp_s_dict["tavg"] = temp_avg
        temp_s_dict["tmax"] = temp_max
        start_temps.append(temp_s_dict)

@app.route("/api/v1.0/<start>/<end>")
def max_temp_start(start, end):

    session = Session(engine)

    start_date = start
    end_date = end
    stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    session.close()

    start_end_temps = []
    for temp_min, temp_avg, temp_max in stats:
        temp_s_e_dict = {}
        temp_s_e_dict["tmin"] = temp_min
        temp_s_e_dict["tavg"] = temp_avg
        temp_s_e_dict["tmax"] = temp_max
        start_end_temps.append(temp_s_e_dict)

    return jsonify(start_end_temps)

if __name__ == "__main__":
    app.run(debug=True)