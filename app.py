import sys
from flask_migrate import Migrate
from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://postgres:6422@localhost:5432/todos"

db = SQLAlchemy(app)

migrate = Migrate(app, db)


class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    completed = db.Column(db.BOOLEAN, nullable=False, default=False)
    list_id = db.Column(db.Integer, db.ForeignKey('todolists.id'), nullable=False)

    def __repr__(self):
        return f"{self.id} is {self.description}"


class ToDOLists(db.Model):
    __tablename__ = "todolists"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    todos = db.relationship(Todo, backref="list", lazy=True)


@app.route('/')
def index():
    return redirect(url_for('get_list_todos', list_id=3))


@app.route('/lists/<list_id>')
def get_list_todos(list_id):
    return render_template('index.html', lists=ToDOLists.query.all(),
                           active_list=ToDOLists.query.get(list_id),
                           todos=Todo.query.filter_by(list_id=list_id).order_by('id').all())


@app.route('/todos/create', methods=['post'])
def create():
    error = False
    body = {}
    try:
        description = request.get_json()['description']
        list_id = request.get_json()['list_id']
        todo = Todo(description=description, list_id=list_id)
        db.session.add(todo)
        db.session.commit()
        body['description'] = todo.description
        body['id'] = todo.id
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if not error:
        return jsonify({
            'description': body['description'],
            'id': body['id']
        })
    else:
        abort(400)


@app.route('/todos/<todo_id>/set-complete', methods=['POST'])
def todo_set_complete(todo_id):
    try:
        completed = request.get_json()['completed']
        todo = Todo.query.get(todo_id)
        todo.completed = completed
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('index'))


@app.route('/todos/<todo_id>/delete', methods=['POST'])
def delete_todo(todo_id):
    try:
        todo = Todo.query.get(todo_id)
        db.session.delete(todo)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.debug = True
    app.run()
