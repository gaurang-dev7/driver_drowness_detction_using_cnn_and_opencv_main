from logging import error
import MySQLdb
from flask import Flask,render_template,request,redirect,url_for,session
from flask_mysqldb import MySQL
from mysql.connector import cursor 
import re
from werkzeug import useragents
import gui3
import drowsy_predict
import logging
import threading
import time


app = Flask (__name__,template_folder='web_login_registor')
app.secret_key='0000'

app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='dev__7'
app.config['MYSQL_PASSWORD']='0000'
app.config['MYSQL_DB']='finalproject'

mysql=MySQL(app)
@app.route('/home')
def home():
    if 'loggedin' in session:
        return render_template('home.html',username=session['username'])
    return redirect(url_for('login'))
    

@app.route('/login',methods=['GET','POST'])
def login():
    msg=''
    # return render_template('index.html',msg='')
    if request.method=='POST' and 'username' in request.form and 'password' in request.form:
        username=request.form['username']
        password=request.form['password']
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('select * from accounts where username=%s and password=%s',(username,password))
        account=cursor.fetchone()
        if account:
            session['loggedin']=True
            session['id']= account['id']
            session['username']=account['username']
            msg='Login successfull!'
            return redirect(url_for('home'))
            # return render_template('login.html',msg=msg)
        else:
            msg='Incorrect username/password'
    



    return render_template('login.html',msg=msg)


@app.route('/logout',methods=['GET','POST'])
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/register',methods=['GET','POST'])
def register():
    msg=''
    if request.method=='POST' and 'fullname' in request.form and  'username' in request.form and 'password' in request.form and 'email' in request.form:
        fullname=request.form['fullname']
        username=request.form['username']
        password=request.form['password']
        email=request.form['email']


        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("""SELECT * FROM accounts WHERE username =%s""",(username,))
        
        # cursor.execute('SELECT * FROM accounts WHERE username = %s', (email))
        account = cursor.fetchone()
        

        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            
            cursor.execute("""INSERT INTO accounts VALUES (NULL, %s, %s, %s, %s)""", (fullname,username, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'

    elif request.method=='POST':
        msg='Plese fill out the form!'
    
    return render_template('register.html',msg=msg)


@app.route('/profile')
def profile():
    if 'loggedin' in session:
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        return render_template('profile.html', account=account)
    return redirect(url_for('login'))

@app.route('/dfd')
def dfd():
    if 'loggedin' in session:
        
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        print(account)
        
        def thread_fuction():
            drowsy_predict.main()
            
        try:
            threading.Thread.start(thread_fuction())
        except:
            print("thread not stated")
            

    return redirect(url_for('home'))


if __name__=='__main__':
    app.run(debug=True)

    
