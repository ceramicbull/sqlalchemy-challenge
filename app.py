# Import the dependencies.
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify






#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base=automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measure=Base.classes.measurement
stat=Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    #session
    session = Session(engine)

    """Return the latest year worth of observations: dates and precipitation"""
    # Query last 12 months of precipitation data
    # find most recent date
    last_row=session.query(measure).order_by(measure.id.desc()).first()
    last_row.date
    #calclulate target date 1 year earlier
    last_date=dt.datetime.strptime(last_row.date, '%Y-%m-%d')
    target_date=last_date-dt.timedelta(days=365)
    #perform the query
    year_prcp=session.query(measure.date,measure.prcp).\
        filter(measure.date.between(\
        func.strftime('%Y-%m-%d', target_date),
        func.strftime('%Y-%m-%d', last_date))).all()

    session.close()

    #store info in list of dictionaries for JSON
    all_prcp=[]
    for date, prcp in year_prcp:
        prcp_dict={}
        prcp_dict[date]=prcp
        all_prcp.append(prcp_dict)


    return jsonify(all_prcp)



@app.route("/api/v1.0/stations")
def stations():
    #session
    session = Session(engine)
    
    """Return information about stations including designation, name, latitude, longitude, and elevation."""
    #Query table info
    results=session.query(stat.station,
                        stat.name,
                        stat.latitude,
                        stat.longitude,
                        stat.elevation).all()
    
    session.close()

    ##store info in list of dictionaries for JSON
    all_stations=[]
    for station,name,latitude,longitude,elevation in results:
        station_dict={}
        station_dict["station"]=station
        station_dict["name"]=name
        station_dict["latitude"]=latitude
        station_dict["longitude"]=longitude
        station_dict["elevation"]=elevation
        all_stations.append(station_dict)
    
    return jsonify(all_stations)



@app.route("/api/v1.0/tobs")
def tobs():
    #session
    session = Session(engine)

    """Return information about tobs (Temperature Observations) from the most active station (USC00519281) over the past year."""
    # Query last 12 months of tobs data
    # find most recent date
    last_row=session.query(measure).order_by(measure.id.desc()).first()
    last_row.date
    #calclulate target date 1 year earlier
    last_date=dt.datetime.strptime(last_row.date, '%Y-%m-%d')
    target_date=last_date-dt.timedelta(days=365)
    #perform the query
    year_tobs=session.query(measure.date,measure.tobs).\
        filter(measure.station=='USC00519281',
               measure.date.between(\
                func.strftime('%Y-%m-%d', target_date),
                func.strftime('%Y-%m-%d', last_date))).all()
    
    session.close()

    #store info in list of dictionaries for JSON
    all_tobs=[]
    for date, tobs in year_tobs:
        tobs_dict={}
        tobs_dict[date]=tobs
        all_tobs.append(tobs_dict)


    return jsonify(all_tobs)


@app.route("/api/v1.0/<start>")
def tobs_start(start):
    """Return the minimum temperature, the average temperature, and the maximum temperature for a period following a specified start date (format: yyyy-mm-dd)."""
    start_date=start.replace(" ", "")

    #session
    session = Session(engine)

    # Query tobs data
    # find most recent date
    last_row=session.query(measure).order_by(measure.id.desc()).first()
    last_row.date
    #perform the query
    range_tobs=session.query(measure.date,func.max(measure.tobs),func.avg(measure.tobs),func.min(measure.tobs)).\
        filter(measure.date.between(\
                start_date,
                last_row.date)).\
        group_by(measure.date).\
        order_by(measure.date).all()
    
    session.close()

    #store info in list of dictionaries for JSON
    dyn_tobs=[]
    for date, tmin, tavg, tmax in range_tobs:
        tobs_dict={}
        tobs_dict["Date"]=date
        tobs_dict["TMIN"]=tmin
        tobs_dict["TAVG"]=tavg
        tobs_dict["TMAX"]=tmax
        dyn_tobs.append(tobs_dict)


    return jsonify(dyn_tobs)


@app.route("/api/v1.0/<start>/<end>")
def tobs_range(start,end):
    """Return the minimum temperature, the average temperature, and the maximum temperature for a period following a specified start date (format: yyyy-mm-dd)."""
    start_date=start.replace(" ", "")
    end_date=end.replace(" ", "")

    #session
    session = Session(engine)

    # Query tobs data
    #perform the query
    range_tobs=session.query(measure.date,func.max(measure.tobs),func.avg(measure.tobs),func.min(measure.tobs)).\
        filter(measure.date.between(\
                start_date,
                end_date)).\
        group_by(measure.date).\
        order_by(measure.date).all()
    
    session.close()

    #store info in list of dictionaries for JSON
    dyn_tobs=[]
    for date, tmin, tavg, tmax in range_tobs:
        tobs_dict={}
        tobs_dict["Date"]=date
        tobs_dict["TMIN"]=tmin
        tobs_dict["TAVG"]=tavg
        tobs_dict["TMAX"]=tmax
        dyn_tobs.append(tobs_dict)


    return jsonify(dyn_tobs)


if __name__ == "__main__":
    app.run(debug=True)
