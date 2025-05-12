from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import cv2
from drawing_app.core import DrawingApp
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Disables the message
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'   # Suppresses other TensorFlow info

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['UPLOAD_FOLDER'] = 'static/drawings'

# Database setup
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db_connection() as conn:
        conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        ''')
        conn.execute('''
        CREATE TABLE IF NOT EXISTS drawings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        conn.commit()

init_db()

# Routes
@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('desktop'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        with get_db_connection() as conn:
            existing_user = conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
            if existing_user:
                flash('Username already exists. Please choose another.', 'error')
                return redirect(url_for('register'))
            
            hashed_password = generate_password_hash(password)
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', 
                         (username, hashed_password))
            conn.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        with get_db_connection() as conn:
            user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            
            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                flash('Login successful!', 'success')
                return redirect(url_for('desktop'))
            else:
                flash('Invalid username or password.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/desktop')
def desktop():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('desktop.html', username=session['username'])

@app.route('/view_drawings')
def view_drawings():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    with get_db_connection() as conn:
        drawings = conn.execute('''
            SELECT * FROM drawings 
            WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (session['user_id'],)).fetchall()
    
    return render_template('view_drawings.html', drawings=drawings)

@app.route('/drawing')
def drawing():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('drawing.html')

@app.route('/run_drawing_app')
def run_drawing_app():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        drawing_app = DrawingApp()
        saved_image = drawing_app.run()
        
        if saved_image is not None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{session['user_id']}_{timestamp}.png"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            cv2.imwrite(filepath, saved_image)
            
            with get_db_connection() as conn:
                conn.execute('''
                    INSERT INTO drawings (user_id, filename, created_at)
                    VALUES (?, ?, ?)
                ''', (session['user_id'], filename, datetime.datetime.now()))
                conn.commit()
            
            flash('Drawing saved successfully!', 'success')
        
        return redirect(url_for('desktop'))
    
    except Exception as e:
        flash(f'Error running drawing app: {str(e)}', 'error')
        return redirect(url_for('desktop'))
    

if __name__ == '__main__':
    app.run(debug=True)