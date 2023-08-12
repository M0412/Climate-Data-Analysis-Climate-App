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
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Define a functions that retrieves data for the past twelve months 
def past_year_data():
    
    # Find the most recent date in the data set.
    most_recent_date = session.query(func.max(Measurement.date)).first()[0]

    # Calculate the date one year from the last date in data set
    start_date = dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days=365)

# Close the session                   
    session.close()

    # Return the date
    return(start_date)

# Home page
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitiation():
      
      # Create our session (link) from Python to the DB
       session = Session(engine)
       
       # Retrieving percipitation data for the last 12 months
       precipitation = session.query(Measurement.date, Measurement.prcp).\
                                order_by(Measurement.date.desc()).\
                                filter(Measurement.date >= past_year_data()).all()
      # Close our session (link) from Python to the DB
       session.close()

       print(precipitation)
    
     # Converting result into a dictionary
       Precipitation = []
       for date, prcp in precipitation:
        prcp_dict = {}
        prcp_dict[date] = prcp
        Precipitation.append(prcp_dict)
    
    # Jsonify the list
       return jsonify(Precipitation)

@app.route("/api/v1.0/stations")
def stations():
     
    # Create our session (link) from Python to the DB
     session = Session(engine)   

     # Query stations
     stations = session.query(Station.station).all()

    # Close session
     session.close()

    # Convert list of tuples into normal list
     Stations_list = list(np.ravel(stations))

    # Jsonify the list
     return jsonify(Stations_list)

@app.route("/api/v1.0/tobs")
def tops():
     
    # Create our session (link) from Python to the DB
     session = Session(engine)   

     # Query the dates and temperature observations of the most-active station for the past 12 months
     start_date = '2016, 8, 23'
     Tobs = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= start_date).\
             filter(Measurement.station == 'USC00519281').all()
    
    # Close the session
     session.close()
     
    # Create a dictionary from the row data and append to a list of date and temp 
     tobs_list=[]
        
     for date, tobs in Tobs:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs
        tobs_list.append(tobs_dict)

    # Jsonify the list
     return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temp(start=None, end=None):
     
    # Create our session (link) from Python to the DB
     session = Session(engine)

     # Retrieving min, max, and avg temperature for a specified start-end date 
     if end != None:
        temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).filter(
            Measurement.date <= end).all()
        
     # Retrieving min, max, and avg temperature for a specified start date only 
     else:
        temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).all()
        
     # Close the session
     session.close()   
    
    # Create a dictionary from the row data and append to a list of min, avg, and max temperature
     temp_list =[]
    
     for min_temp, avg_temp, max_temp in temp_data:
        temp_dict = {}
        temp_dict["Min_temp"] = min_temp
        temp_dict["Avg_temp"] = avg_temp
        temp_dict["Max_temp"] = max_temp
        temp_list.append(temp_dict)

    # Jsonify the list
     return jsonify(temp_list)

if __name__ == '__main__':
    app.run(debug=True)