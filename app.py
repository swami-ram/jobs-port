from flask import Flask, render_template, request, redirect, session
import mysql.connector
import os
from werkzeug.utils import secure_filename 

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = "jobportal123"

# Database Connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345678",   # Change this
    database="jobportal"
)


cursor = db.cursor(buffered=True)

# Home Page
@app.route('/')
def home():
    return render_template('index.html')


# Register
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        sql = "INSERT INTO users(name,email,password) VALUES(%s,%s,%s)"
        values = (name, email, password)

        cursor.execute(sql, values)
        db.commit()

        return redirect('/login')

    return render_template('register.html')


# Login
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        sql = "SELECT * FROM users WHERE email=%s AND password=%s"
        values = (email, password)

        cursor.execute(sql, values)

        user = cursor.fetchone()

        if user:
            session['user'] = email
            return redirect('/jobs')
        else:
            return "Invalid Login"

    return render_template('login.html')



# Show Jobs
@app.route('/jobs')
def jobs():

    cursor.execute("SELECT * FROM jobs")

    jobs_data = cursor.fetchall()

    return render_template(
        'jobs.html',
        jobs=jobs_data
    )


# Apply Job
@app.route('/apply/<int:id>')
def apply(id):

    if 'user' not in session:
        return redirect('/login')

    email = session['user']

    cursor.execute(
        "SELECT * FROM applications WHERE user_email=%s AND job_id=%s",
        (email, id)
    )

    existing = cursor.fetchone()

    if existing:
        return "You already applied for this job."

    cursor.execute(
        "INSERT INTO applications(user_email, job_id) VALUES(%s,%s)",
        (email, id)
    )

    db.commit()

    return redirect('/my-applications')
@app.route('/my-applications')
def my_applications():

    if 'user' not in session:
        return redirect('/login')

    email = session['user']

    cursor.execute("""
        SELECT applications.id,
               jobs.title,
               jobs.company,
               jobs.location
        FROM applications
        JOIN jobs ON applications.job_id = jobs.id
        WHERE applications.user_email = %s
    """, (email,))

    data = cursor.fetchall()

    return render_template('my_applications.html', applications=data)
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/upload', methods=['POST'])
def upload():
    if 'resume' not in request.files:
        return "No file selected"

    file = request.files['resume']

    if file.filename == '':
        return "No file selected"

    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    return "Resume Uploaded Successfully"

print("WITHDRAW ROUTE LOADED")
@app.route('/withdraw/<int:id>')
def withdraw(id):

    if 'user' not in session:
        return redirect('/login')

    email = session['user']

    cursor.execute("""
        DELETE FROM applications
        WHERE id=%s AND user_email=%s
    """, (id, email))

    db.commit()

    return redirect('/my-applications')



@app.route('/admin/applications')
def admin_applications():

    if 'user' not in session:
        return redirect('/login')

    cursor.execute("""
        SELECT applications.id,
               applications.user_email,
               jobs.title,
               jobs.company,
               jobs.location
        FROM applications
        JOIN jobs ON applications.job_id = jobs.id
    """)

    data = cursor.fetchall()

    return render_template('admin_applications.html', applications=data)

@app.route('/admin', methods=['GET', 'POST'])
def admin():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        if username == "root" and password == "12345678":
            return redirect('/dashboard')   # ✅ HERE IT IS CORRECT

    return render_template('admin_login.html')

# Run App
if __name__ == '__main__':
    app.run(debug=True)

