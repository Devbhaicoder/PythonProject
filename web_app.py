from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

@app.route("/")
def home():
    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()

    cursor.execute("SELECT name, datetime FROM attendance ORDER BY datetime DESC")
    data = cursor.fetchall()

    conn.close()
    return render_template("index.html", data=data)

app.run(debug=True)