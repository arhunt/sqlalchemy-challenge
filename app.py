import numpy as np
import datetime as dt
from flask import Flask, jsonify

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, or_, and_

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# We can view all of the classes that automap found
Base.classes.keys()

# Save references to each table
msmnt = Base.classes.measurement
stats = Base.classes.station

# Flask Setup
app = Flask(__name__)

# Flask Routes

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Honolulu Climate App Home Page<br/><br>"
        f"Available Routes:<br/></br>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/></br>"
        f"/api/v1.0/startdate<br/>"
        f"/api/v1.0/startdate/enddate<br/></br>"
        f"Notes:</br>"
        f"Enter startdate, enddate in form YYYY-MM-DD </br>"
        f"Dates are inclusive"
    )

@app.route("/api/v1.0/precipitation")

def precipitation():
    print('Loading "precipitation"...')

    session = Session(engine)

    # Reproduce query: last 12 months of precipitation data
    maxdatefind = session.query(func.max(msmnt.date))
    maxdate = maxdatefind[0][0]
    mindate = f'{int(maxdate[0:4])-1}{maxdate[4:10]}'
    datesprcps = session.query(msmnt.date, msmnt.prcp).filter(msmnt.date >= mindate)

    # Create dictionary with dates@0 as key and prcp@1 as value:
    dateprcpdict = {}
    for row in datesprcps:
        dateprcpdict[row[0]] = row[1]

    session.close()   

    # Return json
    return jsonify(dateprcpdict)


@app.route("/api/v1.0/stations")

def stations():
    print('Loading "stations"...')

    session = Session(engine)

    # Call stations table and place info into dictionary
    stationsdicts = []
    data = engine.execute("SELECT * FROM Station")
    for record in data:
        stationsdict = {}
        stationsdict['Station'] = record[1]
        stationsdict['Name'] = record[2]
        stationsdict['Latitude'] = record[3]
        stationsdict['Longitude'] = record[4]
        stationsdict['Elevation'] = record[5]
        stationsdicts.append(stationsdict)
    
    session.close()
    
    # Return json
    return jsonify(stationsdicts)


@app.route("/api/v1.0/tobs")

def tobs():
    print('Loading "tobs"...')

    session = Session(engine)
    
    # Find the most active station (highest quantity of measurements)
    maxstatfind = session.query(msmnt.station).\
        group_by(msmnt.station).\
        order_by(func.count(msmnt.station).desc()).first()
    maxstation = maxstatfind[0]

    # Find the date from 12 months ago
    lastdatefind = session.query(func.max(msmnt.date))
    lastdate = lastdatefind[0][0]
    firstdate = f'{int(lastdate[0:4])-1}{lastdate[4:10]}'
    
    # Query the dates and station
    datestobs = session.query(msmnt.date, msmnt.tobs).\
        filter(and_(msmnt.date >= firstdate,\
        msmnt.station == maxstation))

    # Place results in dictionary
    datetobsdict = {}
    for row in datestobs:
        datetobsdict[row[0]] = row[1]

    session.close()

    # Return json
    return jsonify(datetobsdict)


@app.route("/api/v1.0/<start>")

def start_stats(start):
    print(f'Loading data for {start} forward...')

    session = Session(engine)

    # Order temps to find min
    mintempfind = session.query(msmnt.tobs).\
        filter(msmnt.date >= start).\
        order_by(msmnt.tobs).first()
    # Order temps desc to find max
    maxtempfind = session.query(msmnt.tobs).\
        filter(msmnt.date >= start).\
        order_by(msmnt.tobs.desc()).first()
    # Average
    avgtempfind = session.query(func.avg(msmnt.tobs)).\
        filter(msmnt.date >= start)
    # Create dictionary with data
    startdatedict = {"TMIN":mintempfind[0],\
        "TAVG":round(avgtempfind[0][0],1),\
        "TMAX":maxtempfind[0]}

    session.close()

    # Return json
    return jsonify(startdatedict)


@app.route("/api/v1.0/<start>/<end>")

def dates_stats(start, end):
    print(f'Loading data for {start} through {end}...')

    session = Session(engine)

    # Order temps to find min
    mintempfind = session.query(msmnt.tobs).\
        filter(and_(msmnt.date >= start), msmnt.date <= end).\
        order_by(msmnt.tobs).first()
    # Order temps desc to find max
    maxtempfind = session.query(msmnt.tobs).\
        filter(and_(msmnt.date >= start), msmnt.date <= end).\
        order_by(msmnt.tobs.desc()).first()
    # Average
    avgtempfind = session.query(func.avg(msmnt.tobs)).\
        filter(and_(msmnt.date > start, msmnt.date <= end))
    # Create dictionary with data
    twodatesdict = {"TMIN":mintempfind[0],\
        "TAVG":round(avgtempfind[0][0],1),\
        "TMAX":maxtempfind[0]}

    session.close()

    # Return json
    return jsonify(twodatesdict)

# End
if __name__ == '__main__':
    app.run(debug=True)