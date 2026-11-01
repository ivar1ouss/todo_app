from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Task
from forms import TaskForm
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def get_grouped_tasks():
    tasks = Task.query.order_by(Task.deadline).all()

    now = datetime.now()
    today_end = now.replace(hour=23, minute=59, second=59)
    week_end = today_end + timedelta(days=(6 - now.weekday()))

    groups = {
        'overdue': [],
        'today': [],
        'week': [],
        'later': [],
        'done': []
    }

    for task in tasks:
        if task.is_done:
            groups['done'].append(task)
        elif task.is_overdue:
            groups['overdue'].append(task)
        elif task.deadline <= today_end:
            groups['today'].append(task)
        elif task.deadline <= week_end:
            groups['week'].append(task)
        else:
            groups['later'].append(task)

    return groups


@app.route('/')
def index():
    groups = get_grouped_tasks()
    total = Task.query.count()
    completed = Task.query.filter_by(is_done=True).count()
    return render_template('index.html', groups=groups, total=total, completed=completed)


@app.route('/add', methods=['GET', 'POST'])
def add():
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(
            title=form.title.data,
            description=form.description.data,
            deadline=form.deadline.data,
            priority=form.priority.data
        )
        db.session.add(task)
        db.session.commit()
        flash('Задача добавлена!', 'success')
        return redirect(url_for('index'))
    return render_template('edit.html', form=form, title="Добавить задачу")


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    task = Task.query.get_or_404(id)
    form = TaskForm(obj=task)

    if form.validate_on_submit():
        form.populate_obj(task)
        db.session.commit()
        flash('Задача обновлена!', 'success')
        return redirect(url_for('index'))

    return render_template('edit.html', form=form, title="Редактировать задачу")


@app.route('/toggle/<int:id>')
def toggle(id):
    task = Task.query.get_or_404(id)
    task.is_done = not task.is_done
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/delete/<int:id>')
def delete(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    flash('Задача удалена', 'info')
    return redirect(url_for('index'))

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)