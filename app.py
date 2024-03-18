import datetime
from flask import Flask,redirect,url_for,render_template,request
from flask_sqlalchemy import SQLAlchemy
import qrcode
import requests


app=Flask(__name__)
app.config['SECRET_KEY'] = 'c288b2157916b13s523242q3wede00ba242sdqwc676dfde'
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///test.db'


db = SQLAlchemy(app)

adminemail = "mr.adumatta@gmail.com"


class StudentData(db.Model):
    """Model for user accounts."""
    __tablename__ = 'students'

    id = db.Column(db.Integer,
                   primary_key=True)
    name = db.Column(db.String)
    age = db.Column(db.String)
    studentclass = db.Column(db.String)
    def __repr__(self):
        return '<Student {}>'.format(self.name)
    


class Logs(db.Model):
    """Model for user accounts."""
    __tablename__ = 'studentData'

    id = db.Column(db.Integer,
                   primary_key=True)
    name = db.Column(db.String)
    time = db.Column(db.DateTime, default=datetime.datetime.utcnow())

    def __repr__(self):
        return f'<Student {self.id}>'
    


@app.route('/',methods=['GET','POST'])
def home():
    # get all logs
    logs = Logs.query.all()
    students = StudentData.query.all()
    print(logs)
    
    return render_template('index.html', logs=logs, students=students)

def createQrCode(name):
    host = request.url_root
    img = qrcode.make(f"{host}log/{name}")
    type(img)  # qrcode.image.pil.PilImage
    img.save(f"static/qrcodes/{name}.png")
    print(name)


def notify(recipient, subject, message):
    requests.get(
        'https://prestoghana.com'
        + "/sendPrestoMail?recipient="+recipient+"&subject="
        + subject
        + "&message="
        + message
    )

# fill a form to generate a qr code
@app.route('/new', methods=['GET', 'POST'])
def new():
    print(request)
    print(request.form)
    if request.method == 'POST':
        form = request.form
        newentry = StudentData(name=form['name'], studentclass=form['studentclass'], age = form['age'])
        # id = newentry.id
        createQrCode(newentry.name)
        notify(adminemail, f'NEW STUDENT: {newentry.name}', f'A user account has been created for {newentry} ')
        db.session.add(newentry)
        db.session.commit()

        return redirect(url_for('home'))
    return render_template('form.html')

@app.route('/qr/<int:id>')
def qr(id):
    student = StudentData.query.get_or_404(id)
    return render_template('qr.html', student=student)

@app.route('/log/<int:id>', methods=['GET', 'POST'])
def log(id):
    student = StudentData.query.get_or_404(id)
    newLog = Logs(name = student.name)
    db.session.add(newLog)
    db.session.commit()

    notify(adminemail, f'{newLog.name} LOGGED IN', f'{newLog.name} has logged in at: {newLog.time}' )
    return f"Hello {newLog.name} you have been logged in successfully at {newLog.time}"

@app.route('/logs')
def logs():
    logs = Logs.query.all()
    return render_template('logs.html', logs=logs)

@app.route('/students')
def students():
    students = StudentData.query.all()
    return render_template('students.html', students=students)

@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    student = StudentData.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    return redirect('/students')

# scan the qr code to send an email
# done.

if __name__ == '__main__':
    #DEBUG is SET to TRUE. CHANGE FOR PROD
    app.run(port=5000,debug=True)