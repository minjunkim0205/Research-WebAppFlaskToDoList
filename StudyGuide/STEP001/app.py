from flask import Flask, render_template, request, redirect
import json, os

app = Flask(__name__)
DATA_FILE = 'data/schedule.json'

@app.route('/')
def index():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        tasks = json.load(f)
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add_task():
    task = {
        "date": request.form['date'],
        "task": request.form['task'],
        "start_time": request.form['start_time'],
        "end_time": request.form['end_time']
    }
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    data.append(task)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
