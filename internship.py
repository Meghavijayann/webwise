import mysql.connector
from flask import Flask, render_template, request, redirect, flash, session, url_for

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Megha@2004",
        database="db1"
    )

@app.route('/')
def home():
    return render_template('homepage.html')

@app.route('/sign', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]
        mobile_number = request.form["mobile_number"]

        conn = get_db_connection()
        cursor = conn.cursor()

        sql = "INSERT INTO dbtable1 (username, password, email, mobile_number) VALUES (%s, %s, %s, %s)"
        values = (username, password, email, mobile_number)

        try:
            cursor.execute(sql, values)
            conn.commit()
            flash('Account created successfully!', 'success')
        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'error')
        finally:
            cursor.close()
            conn.close()

        return redirect('/lpage')
    return render_template('signuppage.html')

@app.route('/lpage', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        conn = get_db_connection()
        cursor = conn.cursor(buffered=True)

        sql = "SELECT * FROM dbtable1 WHERE username = %s AND password = %s"
        values = (username, password)
        cursor.execute(sql, values)
        data = cursor.fetchone()

        cursor.close()
        conn.close()

        if data:
            session['username'] = username
            return redirect('/dashboard')
        else:
            flash('Invalid username or password', 'error')
            return redirect('/lpage')

    return render_template('loginpage.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect('/lpage')

    username = session['username']
    conn = get_db_connection()
    cursor = conn.cursor(buffered=True, dictionary=True)
    # Get current user ID
    cursor.execute("SELECT id FROM dbtable1 WHERE username = %s", (username,))
    user = cursor.fetchone()
    user_id = user['id']

    # Add a new task if form is submitted
    if request.method == 'POST':
        task_text = request.form.get('task')
        if task_text:
            cursor.execute("INSERT INTO tasks (user_id, task) VALUES (%s, %s)", (user_id, task_text))
            conn.commit()
            flash('Task added successfully!', 'success')

    # Retrieve tasks
    cursor.execute("SELECT * FROM tasks WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
    tasks = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('dashboard.html', username=username, tasks=tasks)


@app.route('/delete_task/<int:task_id>')
def delete_task(task_id):
    if 'username' not in session:
        return redirect('/lpage')

    username = session['username']
    conn = get_db_connection()
    cursor = conn.cursor(buffered=True)

    # Get user ID
    cursor.execute("SELECT id FROM dbtable1 WHERE username = %s", (username,))
    user = cursor.fetchone()
    user_id = user[0]

    # Delete task only if it belongs to current user
    cursor.execute("DELETE FROM tasks WHERE id = %s AND user_id = %s", (task_id, user_id))
    conn.commit()

    cursor.close()
    conn.close()

    flash('Task deleted successfully!', 'success')
    return redirect('/dashboard')

@app.route('/quiz/<topic>')
def quiz_topic(topic):
    if topic == 'html':
        return render_template('quiz_html.html')
    elif topic == 'css':
        return render_template('quiz_css.html')
    elif topic == 'javascript':
        return render_template('quiz_js.html')
    else:
        flash('Invalid topic selected!', 'error')
        return redirect('/dashboard')

@app.route('/profile')
def profile():
    if 'username' in session:
        username = session['username']
        conn = get_db_connection()
        cursor = conn.cursor(buffered=True)
        sql = "SELECT username, email, mobile_number FROM dbtable1 WHERE username = %s"
        values = (username,)
        cursor.execute(sql, values)
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()

        if user_data:
            return render_template('profile.html', username=user_data[0], email=user_data[1], mobile_number=user_data[2])
        else:
            flash('User details not found', 'error')
            return redirect('/lpage')
    else:
        return redirect('/')

@app.route('/startpage/<domain>')
def startpage(domain):
    return render_template('quiz_page.html', domain=domain.capitalize())

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/lpage')

@app.route('/about')
def about():
    return render_template('about.html')   


@app.route('/video_lectures')
def video_lectures():
    return render_template('video_lectures.html')

@app.route('/sample_images')
def sample_images():
    return render_template('sampleimg.html')

@app.route('/lecture_links')
def lecture_links():
    return render_template('lecture.html')

@app.route('/platforms')
def platforms():
    return render_template('platforms.html')


if __name__ == '__main__':
    app.run(debug=True)
