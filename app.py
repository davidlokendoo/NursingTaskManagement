from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pt_name = db.Column(db.String(200), nullable=False)
    pt_DOB = db.Column(db.DateTime, nullable=False)
    pt_room = db.Column(db.String(200))
    content = db.Column(db.String(200),nullable=False)
    time_due = db.Column(db.Time, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id

@app.route('/', methods=['POST','GET'])
def index():
 
    tasks = Todo.query.order_by(Todo.time_due).all()
    return render_template('index.html', tasks=tasks)

@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return "There was a problem deleting task."
    
@app.route('/update/<int:id>', methods=['POST','GET'])
def update(id):
    task_to_update = Todo.query.get_or_404(id)
    if request.method == 'POST':
        task_to_update.content = request.form['content']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return "There was a problem updating task."    
    else:
        return render_template('update.html', task=task_to_update)
    
@app.route('/new_patient', methods= ['POST','GET'])    
def new_patient():
    if request.method == 'POST':
        pt_name = request.form['pt_name']
        pt_dob = datetime.strptime(request.form['pt_dob'], '%Y-%m-%d').date()
        print(pt_dob)
        print(request.form['pt_dob'])
        content = request.form['content']
        pt_room = request.form['pt_room']
        time_due = datetime.strptime(request.form['time_due'], '%H:%M').time()
        new_task = Todo(pt_name=pt_name,pt_DOB=pt_dob,content=content, time_due=time_due, pt_room = pt_room)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect("/")   
        except:
            return "There was an issue with adding task."
    else:
        return render_template('new_patient.html')

@app.route('/filtered/<int:hour>', methods=['POST', 'GET'])
def filtered(hour):
    filtered_tasks = []
    tasks = Todo.query.all()
    for task in tasks:
        object_time = task.time_due
        #object_time = datetime.strptime(time_due, '%H:%M').time()
        current_time = datetime.now().time()
       
        difference = datetime.combine(datetime.today(), object_time) - datetime.combine(datetime.today(), current_time)
        difference_in_hours = (difference.total_seconds() //60) // 60

        if difference_in_hours < hour:
            filtered_tasks.append(task)
    return render_template('filtered.html', filtered_tasks=filtered_tasks, hour=hour)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True, port=5001)