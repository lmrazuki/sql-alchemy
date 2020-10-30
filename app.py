from flask import Flask, jsonify

# Import Dependencies
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy import func
import datetime as dt

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

app = Flask(__name__)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# function to convert tuple results into dictionary
def Convert(tup, di): 
    for a, b in tup: 
        di.setdefault(b, []).append(a) 
    return di

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start_date><br/>"
        f"/api/v1.0/<start_date>/<end_date>")

@app.route("/api/v1.0/precipitation")
def rainfall():
    session = Session(engine)

    date = dt.datetime(2016, 8, 22)

    results = session.query(func.sum(Measurement.prcp), Measurement.date).\
            order_by(Measurement.date.asc()).filter(Measurement.date > date).\
            group_by(Measurement.date).all()

    dictionary = {}

    Convert(results, dictionary)

    return jsonify(dictionary)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    results = session.query(Station.station, Station.name)

    dictionary = {}

    Convert(results, dictionary)

    return jsonify(dictionary)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    
    date = dt.datetime(2016, 8, 23)

    temp_query = session.query(Measurement.station, Measurement.tobs).\
            filter(Measurement.station == "USC00519281").\
            filter(Measurement.date > date).all()

    temperatures = [result[1] for result in temp_query]

    return jsonify(temperatures)

@app.route("/api/v1.0/<date>")
def date_filter(date):

    session = Session(engine)

    max_query = session.query(Measurement.station, func.max(Measurement.tobs)).\
                filter(Measurement.date > date)
    maximum = [result[1] for result in max_query]

    min_query = session.query(Measurement.station, func.min(Measurement.tobs)).\
                filter(Measurement.date > date)
    minimum = [result[1] for result in min_query]

    avg_query = session.query(Measurement.station, func.avg(Measurement.tobs)).\
                filter(Measurement.date > date)

    average = [result[1] for result in avg_query]

    dictionary = {"Min temp":minimum,"Max temp":maximum,"Average":average}

    return jsonify(dictionary)

@app.route("/api/v1.0/<start_date>/<end_date>")
def date_between(start_date, end_date):

    session = Session(engine)

    max_query = session.query(Measurement.station, func.max(Measurement.tobs)).\
                filter(Measurement.date >= start_date).filter(Measurement.date <= end_date)
    maximum = [result[1] for result in max_query]

    min_query = session.query(Measurement.station, func.min(Measurement.tobs)).\
                filter(Measurement.date >= start_date).filter(Measurement.date <= end_date)
    minimum = [result[1] for result in min_query]

    avg_query = session.query(Measurement.station, func.avg(Measurement.tobs)).\
                filter(Measurement.date >= start_date).filter(Measurement.date <= end_date)

    average = [result[1] for result in avg_query]

    dictionary = {"Min temp":minimum,"Max temp":maximum,"Average":average}

    return jsonify(dictionary)

if __name__ == '__main__':
    app.run(debug=True)