import os
import sqlite3
from flask import Flask, render_template, request, redirect, session, url_for, flash, g

app = Flask(__name__)
app.secret_key = 'sa78dh2hs91hj879sdh1sdh1'  # 배포시 주의

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'data', 'app.db')

# DB 연결
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

# DB 종료 시 연결 닫기
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db:
        db.close()

# DB 초기화 (테이블 생성)
def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                userid TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                userid TEXT NOT NULL,
                task TEXT NOT NULL,
                date TEXT NOT NULL,
                start_time TEXT,
                end_time TEXT,
                FOREIGN KEY(userid) REFERENCES users(userid)
            )
        ''')
        db.commit()

# 회원가입
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        userid = request.form['userid'].strip()
        password = request.form['password'].strip()

        if not userid or not password:
            flash('아이디와 비밀번호를 모두 입력하세요.')
            return redirect(url_for('register'))

        db = get_db()
        cursor = db.cursor()

        # 중복 검사
        cursor.execute('SELECT * FROM users WHERE userid = ?', (userid,))
        if cursor.fetchone():
            flash('이미 존재하는 사용자입니다.')
            return redirect(url_for('register'))

        # 평문 비밀번호 저장 (연습용)
        cursor.execute('INSERT INTO users (userid, password) VALUES (?, ?)', (userid, password))
        db.commit()

        flash('회원가입 완료! 로그인하세요.')
        return redirect(url_for('login'))

    return render_template('register.html')

# 로그인
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userid = request.form['userid'].strip()
        password = request.form['password'].strip()

        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users WHERE userid = ?', (userid,))
        user = cursor.fetchone()

        if user and user['password'] == password:
            session['userid'] = userid
            return redirect(url_for('index'))
        else:
            flash('아이디 또는 비밀번호가 틀렸습니다.')
            return redirect(url_for('login'))

    return render_template('login.html')

# 로그아웃
@app.route('/logout')
def logout():
    session.pop('userid', None)
    flash('로그아웃 되었습니다.')
    return redirect(url_for('login'))

# 메인 페이지 (할일 리스트)
@app.route('/')
def index():
    if 'userid' not in session:
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM tasks WHERE userid = ? ORDER BY date, start_time', (session['userid'],))
    tasks = cursor.fetchall()

    return render_template('index.html', tasks=tasks, userid=session['userid'])

# 할일 추가
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

    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO tasks (userid, task, date, start_time, end_time)
        VALUES (?, ?, ?, ?, ?)
    ''', (session['userid'], task_text, date, start_time or None, end_time or None))
    db.commit()

    return redirect(url_for('index'))

if __name__ == '__main__':
    os.makedirs(os.path.join(BASE_DIR, 'data'), exist_ok=True)
    init_db()
    app.run(debug=True)
