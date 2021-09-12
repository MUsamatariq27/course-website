from flask import Flask, flash, redirect, render_template, request, session, abort, url_for, g
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text


DATABASE = './assignment3.db'

global student_true
student_true = False

def get_db():
    # if there is a database, use it
    db = getattr(g, '_database', None)
    if db is None:
        # otherwise, create a database to use
        db = g._database = sqlite3.connect(DATABASE)
    return db

# converts the tuples from get_db() into dictionaries
# (don't worry if you don't understand this code)
def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))

# given a query, executes and returns the result
# (don't worry if you don't understand this code)
def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

app = Flask(__name__)
app.secret_key=b'nabil'

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        # close the database if we are connected to it
        db.close()

@app.route('/')
def landing_page():
    print(session)
    if 'utorid' in session:
        return render_template('home.html')
    return render_template('landing_page.html')

@app.route('/student_login')
def student_login():
    return render_template('student_login.html')

@app.route('/instructor_login')
def instructor_login():
    return render_template('instructor_login.html')

@app.route('/student_auth',methods=['POST'])
def student_auth():
    if request.method=='POST':
        query = 'SELECT * FROM students'
        db = get_db()
        db.row_factory = make_dicts

        items = []
        for item in query_db(query):
            #print(item)
            if item['utorid']==request.form['username']:
                if item['password']==request.form['password']:
                    global student_true
                    student_true = True
                    session['utorid']=request.form['username']
                    db.close()

                    return render_template('home.html')
                flash('Invalid Credentials')
        flash('Invalid Credentials') # create alert box
        return redirect(url_for('student_login'))

@app.route('/instructor_auth',methods=['POST'])
def instructor_auth():
    if request.method=='POST':
        print(request.form)
        query = 'SELECT * FROM instructors'
        db = get_db()
        db.row_factory = make_dicts

        items = []
        for item in query_db(query):
            #print(item)
            if item['utorid']==request.form['username']:
                if item['password']==request.form['password']:
                    global student_true
                    student_true = False
                    session['utorid']=request.form['username']
                    db.close()
				

                    return render_template('home.html')
                flash('Invalid Credentials') # create alert box
        flash('Invalid Credentials')
        return redirect(url_for('instructor_login'))

@app.route('/grades', methods=['GET'])
def grades():
    # global student_true
    if 'utorid' in session and student_true==True:
        db = get_db()
        db.row_factory = make_dicts
        print(session)
        items = query_db('SELECT * FROM grades WHERE utorid = ?', [session['utorid']])
        db.close()
        return render_template('grades_st.html', items=items) 
        return render_template('grades_st.html', [])
    #return render_template('grades.html', [])
    else:
        db = get_db()
        db.row_factory = make_dicts
        print(session)
        items = query_db('SELECT * FROM grades') 
        db.close()
        # print(student_true)
        return render_template('grades_ins.html', items=items)
        return render_template('grades_ins.html', [])

@app.route('/edit_marks', methods=['GET', 'POST'])
def edit_marks():
	# db = get_db()
	# db.row_factory = make_dicts
	# cur = db.cursor()
	return render_template('edit_marks.html')
    # global student_true
	# edit_marks=request.form
	# if 'utorid' in session :
		# if request.form =='POST':
			# quiz1=request.form['q1']
			# quiz2=request.form['q2']
			# quiz3=request.form['q3']
			# assignment1=request.form['a1']
			# assignment2=request.form['a2']
			# student_id=request.form['student_utorid']

			# print(quiz1)
			# print(student_id)

			# updateSQL="""UPDATE grades 
					# SET q1 = '{}', q2 = '{}', q3 = '{}', a1 = '{}', a2 = '{}'
					# WHERE utorid = '{}' """.format(quiz1, quiz2, quiz3, assignment1, assignment2, student_id);
					
			# cur.execute(updateSQL)
			# db.commit()
			# cur.close()
			# db.engine.execute(text(updateSQL))
			# db.close()
		# return render_template('grades_ins.html')
			# return 
		#(url_for('grades_ins'), [])\
		# return render_template('grades_ins.html', [])
		
		
		
@app.route('/logout')
def logout():
    session.pop('utorid')
    return redirect(url_for('landing_page'))

@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/newuser', methods=['GET', 'POST'])
def newuser():
    db = get_db()
    db.row_factory = make_dicts
    cur = db.cursor()

    newuser=request.form
	
    if request.method=='POST':
        firstname=request.form['firstname']
        lastname=request.form['lastname']
        utorid=request.form['utorid']
        password=request.form['password']
		 
        
        tablename =''
        if request.form.get('students'):
            tablename='students'
        else:
            tablename='instructors'
        #tablename = 'students' if request.form['students'] == 'checked' else 'instructors'
        updateSQL="""INSERT INTO {} (firstname, lastname, utorid, password) VALUES ('{}', '{}',
                    '{}', '{}')""".format(tablename, firstname, lastname, utorid, password)

        print(updateSQL)
        cur.execute(updateSQL)
        db.commit()
        cur.close()
        return redirect(url_for('landing_page'))


@app.route('/layout')
def layout():
    return render_template('layout.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/calendar')
def calendar():
    return render_template('calendar.html')

@app.route('/news')
def news():
    return render_template('news.html')

@app.route('/assignments')
def assignments():
    return render_template('assignments.html')

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    db = get_db()
    db.row_factory = make_dicts
    cur = db.cursor()

    feedback=request.form
    if 'utorid' in session and student_true==True:
        if request.method=='POST':
            instructor=request.form['instructor']
            like_instructor=request.form['like_instructor']
            recommend_class=request.form['recommend_class']
            like_labs=request.form['like_labs']
            recommend_labs=request.form['recommend_labs']

            updateSQL="""INSERT INTO feedback (instructor, like_instructor, recommend_class, like_labs, recommend_labs) VALUES ('{}', '{}',
                        '{}', '{}', '{}')""".format(instructor, like_instructor, recommend_class, like_labs, recommend_labs)

            print(updateSQL)
            cur.execute(updateSQL)
            db.commit()
            cur.close()
        return render_template('feedback.html')         #redirect(url_for('grades'))

    else:
        db = get_db()
        db.row_factory = make_dicts
        print(session)
        items = query_db('SELECT * FROM feedback WHERE instructor = ?', [session['utorid']])
        db.close()
        return render_template('feedback_instructor.html', items=items)
        return render_template('feedback_instructor.html', [])




@app.route('/Labs')
def labs():
    return render_template('Labs.html')

@app.route('/lectures')
def lectures():
    return render_template('Lectures.html')

@app.route('/resources')
def resources():
    return render_template('resources.html')

@app.route('/tests')
def tests():
    return render_template('tests.html')

if __name__ == '__main__':
    app.run(debug=True)
