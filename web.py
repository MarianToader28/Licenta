import sqlite3
from flask import Flask, render_template, jsonify, request, flash, redirect


app = Flask(__name__)
conn = sqlite3.connect('/var/www/html/FlaskWeb/Measurements.db',check_same_thread=False)
crs = conn.cursor()


def getLastData():
    for data in crs.execute('SELECT * FROM data ORDER BY date_time DESC LIMIT 1'):
        read_time = str(data[0])
        temp = data[1]
        hum = data[2]
        CO = data[3]
       
    return read_time,temp, hum, CO

@app.route('/')
def index():
	read_time,temp, hum, CO = getLastData()
	templateData = {
        'read_time': read_time,
        'temp'  : temp,
        'hum'	: hum,
        'CO'    : CO
    }
    
	return render_template('index.html', **templateData)

@app.route("/graph")
def getRecentMeasurements():
    crs.execute("SELECT date_time, temperature FROM data ORDER BY date_time DESC LIMIT 60")
    data = crs.fetchall()
    labels = [row[0] for row in reversed(data)]
    values = [row[1] for row in reversed(data)]
    crs.execute('SELECT date_time, humidity FROM data ORDER BY date_time DESC LIMIT 60')
    data1 = crs.fetchall()
    labels_hum = [row[0] for row in reversed(data1)]
    values_hum = [row[1] for row in reversed(data1)]
    crs.execute('SELECT date_time, CO FROM data ORDER BY date_time DESC LIMIT 60')
    data2 = crs.fetchall()
    labels_CO = [row[0] for row in reversed(data2)]
    values_CO = [row[1] for row in reversed(data2)]

    return render_template("Graphs.html",labels=labels, values=values,labels_hum=labels_hum, values_hum=values_hum, labels_CO=labels_CO, values_CO=values_CO)


@app.route("/range",methods=["POST","GET"])
def range():
    if request.method == "POST":
        From = request.form['From']
        print(From)
        crs.execute("SELECT date_time, temperature from data WHERE date_time = '{}'".format(From))
        data3 = crs.fetchall()
        new_date = [row[0] for row in reversed(data3)]
        new_temp = [row[1] for row in reversed(data3)]
    return jsonify({'htmlresponse': render_template('response.html',new_date=new_date,new_temp=new_temp)})

#if __name__ == '__main__':
 #  app.run(debug=True,host = '192.168.0.104')
   #app.run(debug=False,host = '0.0.0.0')
   
