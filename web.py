import sqlite3
from flask import Flask, render_template

app = Flask(__name__)
conn = sqlite3.connect('Measurements.db',check_same_thread=False)
crs = conn.cursor()

def getLastData():
    for data in crs.execute('SELECT * FROM data ORDER BY date_time DESC LIMIT 1'):
        #read_time = str(data[0])
        temp = data[1]
        hum = data[2]
    return temp, hum

@app.route("/")
def index():
	temp, hum = getLastData()
	templateData = {
        'temp'	: temp,
        'hum'	: hum
      	
	}
	return render_template('index.html', **templateData)

@app.route("/temp")
def getRecentTemps():
    crs.execute("SELECT date_time, temperature FROM data ORDER BY date_time DESC LIMIT 30")
    data = crs.fetchall()
    labels = [row[0] for row in reversed(data)]
    values = [row[1] for row in reversed(data)]

    return render_template("temperature.html", labels=labels, values=values)

@app.route('/hum')
def getRecentHums():
    crs.execute('SELECT date_time, humidity FROM data ORDER BY date_time DESC LIMIT 30')
    data1 = crs.fetchall()
    labels_hum = [row[0] for row in reversed(data1)]
    values_hum = [row[1] for row in reversed(data1)]

    return render_template("humidity.html", labels_hum=labels_hum, values_hum=values_hum)

if __name__ == '__main__':
   #app.run(debug=True,host = '192.168.0.104')
   app.run(debug=False,host = '0.0.0.0')
   