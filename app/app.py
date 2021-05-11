from typing import List, Dict
import sys
import simplejson as json
from flask import Flask, request, Response, redirect
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
    if len(users) != 0:
        return redirect('/home')
    else:
        return redirect('/')

@app.route('/signup_process', methods=['POST'])
def signup_process():
    name = request.form.get('new_name')
    email = request.form.get('new_email')
    password = request.form.get('new_password')
    cursor = mysql.get_db().cursor()
    cursor.execute("""Insert into `user_Info` (`id`,`Name`,`Email`,`Password`) VALUES (NULL,'{}','{}','{}')"""
                   .format(name,email,password))
    mysql.get_db().commit()
    return "Registration done"



#@app.route('/')
#def get_email():
#    return render_template('index.html')

#@app.route('/', methods=['GET','POST'])
#def login():
#    error = None
#    if request.method == 'POST':
#        mail = request.form['Mail Address']
#        pw = request.form['Password']
#        print(mail, file=sys.stderr)
#        print(pw, file=sys.stderr)
#        cursor2 = mysql.get_db().cursor()
        #cursor2.execute('SELECT Password FROM user_Info where Email = %s', mail)
        #result2 = cursor2.fetchall()

#        cursor2.execute('Select Password from user_Info where Email = %s', (mail, ))
#        pwcheck = cursor2.fetchone()
#        print(pwcheck, file=sys.stderr)
#        if pwcheck[0] == pw:
#            return render_template('login_go.html')
#        else:
#            return render_template('login_fail.html')
#    else:
#        return render_template('didnot.html')

        #cursor1 = mysql.get_db().cursor()
        #cursor1.execute('SELECT Password FROM user_Info where Email = %s', mail)
        #result1 = cursor1.fetchall()
        #cursor2 = mysql.get_db().cursor()
        #cursor2.execute('SELECT Email FROM user_Info where Password = %s', pw)
        #result2 = cursor2.fetchall()
        #if mail != result2[0] or pw != result1[0]:
        #    error = 'Invalid Credentials. Please try again.'
        #    return render_template('login_fail.html')
        #else:
        #    print("valid")
        #    return render_template('login_go.html')

    #return render_template('didnot.html')
    #print("out")
    #return render_template('signup.html', error=error)










@app.route('/result',methods = ['POST', 'GET'])
def result():
    result = request.form
    message = Mail(
        from_email='oguriteja@gmail.com',
        to_emails=request.form['Mail Address'],
        subject='Verification Mail',
        html_content='<strong>Click on the given link to verify and go back to the website</strong>')


    try:
        #print(json.dumps(message.get(), sort_keys=True, indent=4))
        sendgrid_client = SendGridAPIClient(api_key='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')
        response = sendgrid_client.send(message)
        #response = sendgrid_client.client.mail.send.post(request_body=message_json)
        #print('SENDGRID_API_KEY')
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)
    return render_template("result.html", result=result)






#sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
#sg = sendgrid.SendGridAPIClient(apikey='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')
#from_email = Email("test@example.com")
#to_email = To("oguriteja@gmail.com")
#subject = "Sending with SendGrid is Fun"
#content = Content("text/plain", "and easy to do anywhere, even with Python")
#mail = Mail(from_email, to_email, subject, content)
#mail = Mail(from_email, to_email, subject, content)
#response = sg.client.mail.send.post(request_body=mail.get())
#response = sg.send(mail)
#print(response.status_code)
#print(response.body)
#print(response.headers)

#@app.route('/bplayers/new', methods=['GET'])
#def index():
#    return render_template('login.html', title='Login')

@app.route('/home', methods=['GET'])
def home():
    user = {'username': 'Baseball Project'}
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM tblBaseball_Players')
    result = cursor.fetchall()
    return render_template('index_1.html', title='Home', user=user, players=result)


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
