import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement=Base.classes.measurement
Station=Base.classes.station
#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def HomePage():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
        
    )

############# Convert the query results to a dictionary using date as the key and prcp as the value.
################Return the JSON representation of your dictionary.

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    results = session.query(Measurement.date,Measurement.prcp).all()

    session.close()

    prcp_data = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        prcp_data.append(prcp_dict)
        
    return jsonify(prcp_data)

##############Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    results = session.query(Station.station,Station.name).all()

    session.close()

    station_list = []
    for s_id, name in results:
        station_dict = {}
        station_dict["s_id"] = s_id
        station_dict["name"] = name
        station_list.append(station_dict)
        
    return jsonify(station_list)




###############Query the dates and temperature observations of the most active station for the last year of data.
######################Return a JSON list of temperature observations (TOBS) for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    #Recent_Date=session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    Last_Date=dt.date(2017,8,23)-dt.timedelta(days=366)
    Active_station=session.query(Measurement.station).group_by(Measurement.station)\
                    .order_by(func.count(Measurement.station).desc()).first()
    results = session.query(Measurement.station,Measurement.date,Measurement.tobs)\
            .filter(Measurement.station==Active_station[0],Measurement.date>Last_Date).all()

    session.close()

    ActiveStation_TOBS = []
    for name, date, tobs in results:
        tobs_list = {}
        tobs_list["Station name"] = name
        tobs_list["Date"] = date
        tobs_list["tobs"] = tobs
        ActiveStation_TOBS.append(tobs_list)

    return jsonify(ActiveStation_TOBS)


###########################################Return a JSON list of the minimum temperature, the average temperature,
##############and the max temperature for a given start or start-end range.
##################When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.


@app.route("/api/v1.0/<start>")
def start_Date(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    results = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs))\
            .filter(Measurement.date>=start).all()

    session.close()

    TOBS = []
    for TMIN,TMAX,TAVG in results:
        tobs_list = {}
        tobs_list["TMIN"] = TMIN
        tobs_list["TMAX"] = TMAX
        tobs_list["TAVG"] = TAVG
        TOBS.append(tobs_list)

    return jsonify(TOBS)


####################Return a JSON list of the minimum temperature, the average temperature,and the max temperature for a given start or start-end range.
#############################When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start>/<end>")
def startend_Date(start,end):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    results = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs))\
            .filter(Measurement.date>=start,Measurement.date<=end).all()

    session.close()

    TOBS = []
    for TMIN,TMAX,TAVG in results:
        tobs_list = {}
        tobs_list["Minimum Temperature"] = TMIN
        tobs_list["Maximum Temperature"] = TMAX
        tobs_list["Average Temperature"] = TAVG
        TOBS.append(tobs_list)

    return jsonify(TOBS)
if __name__ == '__main__':
    app.run(debug=True)
