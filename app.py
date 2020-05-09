#imort the dependencies
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#Create a engine 
engine = create_engine("sqlite:///Resources/hawaii.sqlite",connect_args={'check_same_thread': False})
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
Base.classes.keys()

# Reflect Database into ORM classes
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

############################ Flask ######################################

from flask import Flask, jsonify

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
app.config["CACHE_TYPE"] = "null"
@app.route("/")
def welcome():
    return (
        f"Welcome to the Hwaii Temperature API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/Startdate/<br/>"  
        f"/api/v1.0/Startdate/Enddate/<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
   """Return the Precipitation as json"""
   precipitation = session.query(Measurement.date, func.avg(Measurement.prcp)).\
               group_by(Measurement.date).all()
   precipitation = pd.DataFrame(precipitation, columns=['date', 'prcp'])
   precipitation.set_index('date', inplace=True)
   return jsonify(precipitation.to_json())


@app.route("/api/v1.0/stations")
def stations():
   """Return the Station Data as json"""
   Station_list = session.query(Station.station, Station.name).\
               group_by(Station.station, Station.name).all()
   return jsonify(Station_list)

@app.route("/api/v1.0/tobs")
def tobs():
   """Return the Station Data as json"""
   ### Get the Temperature for the most Active Station (We found the active station as USC00519281 in Juypter notebook )
   sel = [Measurement.date,
          func.avg(Measurement.tobs)
              ]
        # Retrive One year worth of Temperature data for the most actove station based on last date compute in above cell
   One_Year_Temperature = session.query(*sel).\
            filter(
            Measurement.date <= "2017-08-18",
            Measurement.date >= "2016-08-18",
            Measurement.station=="USC00519281"
        ).\
   group_by(Measurement.date).\
   order_by(Measurement.date).all()

   df_temp = pd.DataFrame(One_Year_Temperature, columns=['date', 'tobs'])
   df_temp.set_index('date', inplace=True)
   
   return jsonify(df_temp.to_json())

@app.route("/api/v1.0/Startdate/<Sdate>")
def Startdate(Sdate):
    """Return the `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start dateas json"""
    sel = [
       func.min(Measurement.tobs),
       func.avg(Measurement.tobs),
       func.max(Measurement.tobs)
      ]
    Temperature_start = session.query(*sel).\
    filter(
    Measurement.date >=Sdate
    ).all()
    
    return jsonify(Temperature_start)


@app.route("/api/v1.0/Startdate/Enddate/<Sdate>,<Edate>")
def Start_End_date(Sdate,Edate):
    """Calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive
       The Url should be like http://127.0.0.1:5000/api/v1.0/Startdate/2010-02-23,2010-02-03
    ."""
    sel = [
       func.min(Measurement.tobs),
       func.avg(Measurement.tobs),
       func.max(Measurement.tobs)
      ]
    Temperature_start_end = session.query(*sel).\
    filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
       
    return jsonify(Temperature_start_end)


if __name__ == "__main__":
    app.run(debug=True)