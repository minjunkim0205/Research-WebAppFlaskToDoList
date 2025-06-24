import os
import json
from flask import Flask, render_template, request, redirect, session, url_for, flash

app = Flask(__name__)
app.secret_key = 'j348fdu4hd2jkehs9'  # 환경변수 등에서 관리 권장

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(BASE_DIR, 'data', 'users.json')
TASKS_FILE = os.path.join(BASE_DIR, 'data', 'tasks.json')

def load_json(file_path):
    if not os.path.exists(file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=4)
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users = load_json(USERS_FILE)
        userid = request.form.get('userid', '').strip()
        password = request.form.get('password', '').strip()

        if not userid or not password:
            flash('아이디와 비밀번호를 모두 입력하세요.')
            return redirect(url_for('register'))

        if userid in users:
            flash('이미 존재하는 사용자입니다.')
            return redirect(url_for('register'))

        users[userid] = {'password': password}  # 평문 저장
        save_json(USERS_FILE, users)

        flash('회원가입 완료! 로그인하세요.')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = load_json(USERS_FILE)
        userid = request.form['userid'].strip()
        password = request.form['password'].strip()

        # 평문 비교
        if userid in users and users[userid]['password'] == password:
            session['userid'] = userid
            return redirect(url_for('index'))
        else:
            flash('아이디 또는 비밀번호가 틀렸습니다.')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('userid', None)
    flash('로그아웃 되었습니다.')
    return redirect(url_for('login'))

@app.route('/')
def index():
    if 'userid' not in session:
        return redirect(url_for('login'))

    tasks_data = load_json(TASKS_FILE)
    user_tasks = tasks_data.get(session['userid'], [])
    return render_template('index.html', tasks=user_tasks, userid=session['userid'])

@app.route('/add', methods=['POST'])
def add_task():
    if 'userid' not in session:
        return redirect(url_for('login'))

    task_text = request.form.get('task', '').strip()
    date = request.form.get('date', '').strip()
    start_time = request.form.get('start_time', '').strip()
    end_time = request.form.get('end_time', '').strip()

    if not task_text or not date:
        flash('할일과 날짜는 필수 입력 항목입니다.')
        return redirect(url_for('index'))

    task = {
        "task": task_text,
        "date": date,
        "start_time": start_time if start_time else None,
        "end_time": end_time if end_time else None
    }

    tasks_data = load_json(TASKS_FILE)
    user_tasks = tasks_data.get(session['userid'], [])
    user_tasks.append(task)
    tasks_data[session['userid']] = user_tasks
    save_json(TASKS_FILE, tasks_data)

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
