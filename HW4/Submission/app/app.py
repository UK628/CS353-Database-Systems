import re  
import os
from flask import Flask, render_template, request, redirect, url_for, session,flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
from datetime import datetime

app = Flask(__name__) 

app.secret_key = 'abcdefgh'
  
app.config['MYSQL_HOST'] = 'db'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'cs353hw4db'
  
mysql = MySQL(app)  

@app.route('/')
def start():
    if 'loggedin' in session:
        return redirect(url_for('tasks'))
    else:
        return redirect(url_for('login'))

@app.route('/login', methods =['GET', 'POST'])
def login():
    if not 'loggedin' in session:
        message = ''
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
            username = request.form['username']
            password = request.form['password']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM User WHERE username = % s AND password = % s', (username, password, ))
            user = cursor.fetchone()
            if user:              
                session['loggedin'] = True
                session['userid'] = user['id']
                session['username'] = user['username']
                session['email'] = user['email']
                message = 'Logged in successfully!'
                return redirect(url_for('tasks'))
            else:
                message = 'Please enter correct email / password !'
        return render_template('login.html', message = message)
    else:
        return redirect(url_for('tasks'))


@app.route('/logout')
def logout():
    if 'loggedin' in session:
        session.clear()
    return redirect(url_for('login'))


@app.route('/register', methods =['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM User WHERE username = % s', (username, ))
        account = cursor.fetchone()
        if account:
            message = 'Choose a different username!'
  
        elif not username or not password or not email:
            message = 'Please fill out the form!'

        else:
            cursor.execute('INSERT INTO User (id, username, email, password) VALUES (NULL, % s, % s, % s)', (username, email, password,))
            mysql.connection.commit()
            message = 'User successfully created!'

    elif request.method == 'POST':

        message = 'Please fill all the fields!'
    return render_template('register.html', message = message)

@app.route('/tasks', methods =['GET', 'POST'])
def tasks():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Task JOIN TaskType on Task.task_type = TaskType.type where user_id = %s', (session['userid'],))
        tasks = cursor.fetchall()
        cursor.execute('SELECT * FROM TaskType')
        taskTypes = cursor.fetchall()
        
        if request.method == 'POST':
            operation = request.form['operation']

            if operation == 'create':
                task_title = request.form['task_title']
                task_description = request.form['task_description']
                task_type = request.form['task_type']
                task_deadline_str = request.form['task_deadline']
                format_str = '%Y-%m-%d %H:%M:%S'
                if task_deadline_str.count(':') != 2:
                    task_deadline_str += ':00'
                task_deadline = datetime.strptime(task_deadline_str.replace('T', ' '), format_str)
                now = datetime.now()
                if task_deadline < now:
                    flash('Please enter a valid deadline that is in the future.')
                    return redirect(url_for('tasks'))
                task_completion_time = None
                task_creation_time = now
                cursor.execute('INSERT INTO Task (title, description, task_type, status, user_id, deadline, done_time, creation_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', (task_title, task_description, task_type, 'Todo', session['userid'], task_deadline, task_completion_time, task_creation_time))
                mysql.connection.commit()

            elif operation == 'edit':
                task_id = request.form['task_id']
                task_title = request.form['task_title']
                task_description = request.form['task_description']
                task_type = request.form['task_type']
                task_deadline_str = request.form['task_deadline']
                format_str = '%Y-%m-%d %H:%M:%S'
                if task_deadline_str.count(':') != 2:
                    task_deadline_str += ':00'
                task_deadline = datetime.strptime(task_deadline_str.replace('T', ' '), format_str)
                now = datetime.now()
                if task_deadline < now:
                    flash('Please enter a valid deadline that is in the future.')
                    return redirect(url_for('tasks'))
                cursor.execute('UPDATE Task SET title = %s, description = %s, task_type = %s, deadline = %s WHERE id = %s AND user_id = %s', (task_title, task_description, task_type, task_deadline, task_id, session['userid']))
                mysql.connection.commit()

            elif operation == 'delete':
                task_id = request.form['task_id']
                cursor.execute('DELETE FROM Task WHERE id = %s AND user_id = %s', (task_id, session['userid']))
                mysql.connection.commit()

            elif operation == 'status':
                task_id = request.form['task_id']
                task_status = request.form['task_status']
                if task_status == 'Done': 
                    task_completion_time = datetime.now()
                else: 
                    task_completion_time =  None
                cursor.execute('UPDATE Task SET status = %s, done_time = %s WHERE id = %s AND user_id = %s', (task_status, task_completion_time, task_id, session['userid']))
                mysql.connection.commit()

            return redirect(url_for('tasks'))

        return render_template('tasks.html', tasks=tasks, taskTypes=taskTypes)
    else:
        return redirect(url_for('login'))


@app.route('/analysis')
def analysis():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        #List the title and latency of the tasks that were completed after their deadlines (for the user).
        cursor.execute('SELECT title, CONCAT( FLOOR(TIMESTAMPDIFF(SECOND, deadline, done_time) / 86400), \' days \', MOD(FLOOR(TIMESTAMPDIFF(SECOND, deadline, done_time) / 3600), 24), \' hours \',MOD(FLOOR(TIMESTAMPDIFF(SECOND, deadline, done_time) / 60), 60), \' minutes \', MOD(TIMESTAMPDIFF(SECOND, deadline, done_time), 60), \' seconds \') as latency FROM Task WHERE user_id=%s AND status="Done" AND done_time > deadline', [session['userid']])
        result1 = cursor.fetchall()

        #Give the average task completion time of the user.
        cursor.execute('SELECT CONCAT( FLOOR(AVG(TIMESTAMPDIFF(SECOND, creation_time, done_time)) / 86400), " days ", MOD(FLOOR(AVG(TIMESTAMPDIFF(SECOND, creation_time, done_time)) / 3600), 24), " hours ",MOD(FLOOR(AVG(TIMESTAMPDIFF(SECOND, creation_time, done_time)) / 60), 60), " minutes ", MOD(AVG(TIMESTAMPDIFF(SECOND, creation_time, done_time)), 60), " seconds ") as avg_time FROM Task WHERE user_id=%s AND status="Done"', [session['userid']])
        result2 = cursor.fetchone()

        #List the number of the completed tasks per task type, in descending order (for the user).
        cursor.execute('SELECT task_type, COUNT(*) as count FROM Task WHERE user_id=%s AND status="Done" GROUP BY task_type ORDER BY count DESC', [session['userid']])
        result3 = cursor.fetchall()

        #List the title and deadline of uncompleted tasks in increasing order of deadlines (for the user).
        cursor.execute('SELECT title, deadline FROM Task WHERE user_id=%s AND status="Todo" ORDER BY deadline ASC', [session['userid']])
        result4 = cursor.fetchall()

        #List the title and task completion time of the top 2 completed tasks that took the most time, in descending order (for the user).
        cursor.execute('SELECT title, CONCAT( FLOOR(TIMESTAMPDIFF(SECOND, creation_time, done_time) / 86400), " days ", LPAD(MOD(FLOOR(TIMESTAMPDIFF(SECOND, creation_time, done_time) / 3600), 24), 2, "0"), " hours ", LPAD(MOD(FLOOR(TIMESTAMPDIFF(SECOND, creation_time, done_time) / 60), 60), 2, "0"), " minutes ", LPAD(MOD(TIMESTAMPDIFF(SECOND, creation_time, done_time), 60), 2, "0"), " seconds ") as completion_time FROM Task WHERE user_id=%s AND status="Done" ORDER BY TIMESTAMPDIFF(SECOND, creation_time, done_time) DESC LIMIT 2', [session['userid']])
        result5 = cursor.fetchall()

        # Close the database connection
        cursor.close()

        # Render the analysis page and pass the query results as variables
        return render_template('analysis.html', result1=result1, result2=result2, result3=result3, result4=result4, result5=result5)
    else:
        return redirect(url_for('login'))


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
