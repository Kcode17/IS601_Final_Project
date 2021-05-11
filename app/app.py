from typing import List, Dict
import sys
import simplejson as json
import random
from flask import Flask, request, Response, redirect, session
from flask import render_template
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor
import sendgrid
import os
from sendgrid.helpers.mail import Mail
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import *

app = Flask(__name__)
mysql = MySQL(cursorclass=DictCursor)
app.secret_key=os.urandom(24)

app.config['MYSQL_DATABASE_HOST'] = 'db'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_PORT'] = 3306
app.config['MYSQL_DATABASE_DB'] = 'Baseball_Players'
#app.config['MAIL_SERVER'] = 'smtp.sendgrid.net'
#app.config['MAIL_PORT'] = 587
#app.config['MAIL_USE_TLS'] = True
#app.config['MAIL_USERNAME'] = 'apikey'
#app.config['SECRET_KEY'] = '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'
#app.config['MAIL_PASSWORD'] = os.environ.get('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')
#app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')

mysql.init_app(app)

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/signup')
def sign_up():
    return render_template('signup.html')

@app.route('/login_check', methods=['POST'])
def login_check():
    email = request.form.get('email')
    password = request.form.get('password')
    cursor = mysql.get_db().cursor()
    cursor.execute("""Select * from `user_Info` where `Email` like '{}' and `Password` like '{}'""".format(email,password))
    users=cursor.fetchall()
    #print(isinstance(users,list),flush=True)
    if len(users) > 0:
        session['userid'] = users[0]
        return redirect('/home')
    else:
        return redirect('/')

#@app.route('/signup_process', methods=['POST'])
#def signup_process():
#    name = request.form.get('new_name')
#    email = request.form.get('new_email')
#    password = request.form.get('new_password')
#    cursor = mysql.get_db().cursor()
#    cursor.execute("""Insert into `user_Info` (`id`,`Name`,`Email`,`Password`) VALUES (NULL,'{}','{}','{}')"""
#                   .format(name,email,password))
#    mysql.get_db().commit()
#    return "Registration done"
def gen_otp():
    return random.randrange(1000,9999)

@app.route('/signup_process', methods=['POST'])
def signup_process():
    session['name'] = request.form.get('new_name')
    session['email'] = request.form.get('new_email')
    session['password'] = request.form.get('new_password')
    session['otp'] = gen_otp()
    message = Mail(
        from_email='oguriteja@gmail.com',
        to_emails=request.form['new_email'],
        subject='Verification Mail',
        html_content="<strong>Here is your OTP for email verification :" + str(session['otp']) + "</strong>")
    sendgrid_client = SendGridAPIClient(api_key=os.environ.get("SENDGRID_API_KEY"))
    response = sendgrid_client.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)
    return render_template('check_otp.html')

@app.route('/check_otp',methods=['POST'])
def check_otp():
    user_otp = request.form.get('otp')
    if str(user_otp) == str(session['otp']):
        name = session['name']
        email = session['email']
        password = session['password']
        cursor = mysql.get_db().cursor()
        cursor.execute("""Insert into `user_Info` (`id`,`Name`,`Email`,`Password`) VALUES (NULL,'{}','{}','{}')"""
                           .format(name,email,password))
        mysql.get_db().commit()
        return redirect('/')
    else:
        return "Verification Failed"






@app.route('/logout')
def logout():
    session.pop('userid')
    return redirect('/')

@app.route('/home', methods=['GET'])
def home():
    if 'userid' in session:
        user = {'username': 'Baseball Project'}
        cursor = mysql.get_db().cursor()
        cursor.execute('SELECT * FROM tblBaseball_Players')
        result = cursor.fetchall()
        return render_template('index_1.html', title='Home', user=user, players=result)
    else:
        return redirect('/')

@app.route('/view/<int:player_id>', methods=['GET'])
def record_view(player_id):
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM tblBaseball_Players WHERE id=%s', player_id)
    result = cursor.fetchall()
    return render_template('view.html', title='View Form', player=result[0])


@app.route('/edit/<int:player_id>', methods=['GET'])
def form_edit_get(player_id):
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM tblBaseball_Players WHERE id=%s', player_id)
    result = cursor.fetchall()
    return render_template('edit.html', title='Edit Form', player=result[0])


@app.route('/edit/<int:player_id>', methods=['POST'])
def form_update_post(player_id):
    cursor = mysql.get_db().cursor()
    inputData = (request.form.get('Name'), request.form.get('Team'), request.form.get('Position'),
                 request.form.get('Height_inches'), request.form.get('Weight_lbs'),
                 request.form.get('Age'), player_id)
    sql_update_query = """UPDATE tblBaseball_Players t SET t.Name = %s, t.Team = %s, t.Position = %s, t.Height_inches = 
    %s, t.Weight_lbs = %s, t.Age = %s WHERE t.id = %s """
    cursor.execute(sql_update_query, inputData)
    mysql.get_db().commit()
    return redirect("/", code=302)

@app.route('/bplayers/new', methods=['GET'])
def form_insert_get():
    return render_template('new.html', title='New Player Form')


@app.route('/bplayers/new', methods=['POST'])
def form_insert_post():
    cursor = mysql.get_db().cursor()
    inputData = (request.form.get('Name'), request.form.get('Team'), request.form.get('Position'),
                 request.form.get('Height_inches'), request.form.get('Weight_lbs'),
                 request.form.get('Age'))
    sql_insert_query = """INSERT INTO tblBaseball_Players (Name,Team,Position,Height_inches,Weight_lbs,Age) VALUES (%s, %s,%s, %s,%s, %s) """
    cursor.execute(sql_insert_query, inputData)
    mysql.get_db().commit()
    return redirect("/", code=302)

@app.route('/delete/<int:player_id>', methods=['POST'])
def form_delete_post(player_id):
    cursor = mysql.get_db().cursor()
    sql_delete_query = """DELETE FROM tblBaseball_Players WHERE id = %s """
    cursor.execute(sql_delete_query, player_id)
    mysql.get_db().commit()
    return redirect("/", code=302)


@app.route('/api/v1/bplayers', methods=['GET'])
def api_browse() -> str:
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM tblBaseball_Players')
    result = cursor.fetchall()
    json_result = json.dumps(result);
    resp = Response(json_result, status=200, mimetype='application/json')
    return resp


@app.route('/api/v1/bplayers/<int:player_id>', methods=['GET'])
def api_retrieve(player_id) -> str:
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM tblBaseball_Players WHERE id=%s', player_id)
    result = cursor.fetchall()
    json_result = json.dumps(result);
    resp = Response(json_result, status=200, mimetype='application/json')
    return resp

@app.route('/api/v1/bplayers/<int:player_id>', methods=['PUT'])
def api_edit(player_id) -> str:
    cursor = mysql.get_db().cursor()
    content = request.json
    inputData = (content['Name'], content['Team'], content['Position'],
                 content['Height_inches'], content['Weight_lbs'],
                 content['Age'],player_id)
    sql_update_query = """UPDATE tblBaseball_Players t SET t.Name = %s, t.Team = %s, t.Position = %s, t.Height_inches = 
        %s, t.Weight_lbs = %s, t.Age = %s WHERE t.id = %s """
    cursor.execute(sql_update_query, inputData)
    mysql.get_db().commit()
    resp = Response(status=200, mimetype='application/json')
    return resp

#@app.route('/api/v1/bplayers', methods=['POST'])
#def api_add() -> str:

#    content = request.json

#    cursor = mysql.get_db().cursor()
#    inputData = (content['Name'], content['Team'], content['Position'],
#                 content['Height_inches'], content['Weight_lbs'], content['Age'])
#    sql_insert_query = """INSERT INTO tblBaseball_Players (Name,Team,Position,Height_inches,Weight_lbs,Age) VALUES (%s,%s, %s,%s, %s,%s) """
#    cursor.execute(sql_insert_query, inputData)
#    mysql.get_db().commit()
#    resp = Response(status=201, mimetype='application/json')
#    return resp

#@app.route('/api/v1/bplayers/<int:player_id>', methods=['DELETE'])
#def api_delete(player_id) -> str:
#    cursor = mysql.get_db().cursor()
#    sql_delete_query = """DELETE FROM tblBaseball_Players WHERE id = %s """
#    cursor.execute(sql_delete_query, player_id)
#    mysql.get_db().commit()
#    resp = Response(status=200, mimetype='application/json')
#    return resp



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
