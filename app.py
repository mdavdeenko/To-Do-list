from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Habit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    progress = db.Column(db.Integer, default=0)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
@login_required
def index():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template('my_index.html', tasks=tasks)


@app.route('/add', methods=['POST'])
@login_required
def add_task():
    task_content = request.form.get('content')
    if task_content:
        new_task = Task(content=task_content, user_id=current_user.id)
        db.session.add(new_task)
        db.session.commit()
        flash('Task added successfully!')
    return redirect(url_for('index'))


@app.route('/delete/<int:id>')
@login_required
def delete_task(id):
    task = Task.query.get_or_404(id)
    if task.user_id == current_user.id:
        db.session.delete(task)
        db.session.commit()
        flash('Task deleted successfully!')
    return redirect(url_for('index'))


@app.route('/complete/<int:id>')
@login_required
def complete_task(id):
    task = Task.query.get_or_404(id)
    if task.user_id == current_user.id:
        task.completed = not task.completed
        db.session.commit()
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password!')
    return render_template('my_login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! You can now login.')
        return redirect(url_for('login'))
    return render_template('my_register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/habits', methods=['GET', 'POST'])
@login_required
def habits():
    if request.method == 'POST':
        habit_name = request.form.get('habit_name')
        if habit_name:
            new_habit = Habit(name=habit_name, user_id=current_user.id)
            db.session.add(new_habit)
            db.session.commit()
            flash('Habit added successfully!')

    user_habits = Habit.query.filter_by(user_id=current_user.id).all()
    return render_template('my_habits.html', habits=user_habits)


@app.route('/delete_habit/<int:id>', methods=['POST'])
@login_required
def delete_habit(id):
    habit = Habit.query.get_or_404(id)
    if habit.user_id == current_user.id:
        db.session.delete(habit)
        db.session.commit()
        flash('Habit deleted successfully!')
    return redirect(url_for('habits'))


@app.route('/update_habit/<int:id>', methods=['POST'])
@login_required
def update_habit(id):
    habit = Habit.query.get_or_404(id)
    if habit.user_id == current_user.id:
        habit.progress += 1
        db.session.commit()
        flash('Habit progress updated!')
    return redirect(url_for('habits'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
