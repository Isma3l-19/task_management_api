# app.py
from flask import Flask, jsonify, request, abort
from flasgger import Swagger
from models import db, Task
from config import Config
from math import ceil
import uuid

# Initialize the Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize Swagger and SQLAlchemy
swagger = Swagger(app)
db.init_app(app)
# Helper function to paginate the query
def paginate(query, page, per_page):
    total_items = query.count()
    total_pages = ceil(total_items / per_page)
    # Correct usage of paginate with the right number of parameters
    items = query.paginate(page=page, per_page=per_page, error_out=False).items
    return {
        "total_items": total_items,
        "total_pages": total_pages,
        "current_page": page,
        "per_page": per_page,
        "items": [item.to_dict() for item in items]
    }


# Route to create a task
@app.route('/tasks', methods=['POST'])
def create_task():
    """
    Create a new task
    ---
    tags:
      - Tasks
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            title:
              type: string
              description: "Title of the task"
            description:
              type: string
              description: "Detailed description of the task"
          required:
            - title
    responses:
      201:
        description: Task created successfully
      400:
        description: Invalid input, object invalid
    """
    if not request.json or not 'title' in request.json:
        abort(400)

    task = Task(
        id=str(uuid.uuid4()),
        title=request.json['title'],
        description=request.json.get('description', "")
    )
    db.session.add(task)
    db.session.commit()

    return jsonify(task.to_dict()), 201

# app.py
@app.route('/tasks', methods=['GET'])
def get_tasks():
    """
    Get the list of all tasks with pagination
    ---
    tags:
      - Tasks
    parameters:
      - name: page
        in: query
        type: integer
        description: Page number
        required: false
        default: 1
      - name: per_page
        in: query
        type: integer
        description: Number of items per page
        required: false
        default: 10
    responses:
      200:
        description: Paginated list of tasks
        schema:
          type: object
          properties:
            total_items:
              type: integer
            total_pages:
              type: integer
            current_page:
              type: integer
            per_page:
              type: integer
            items:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: string
                  title:
                    type: string
                  description:
                    type: string
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    tasks_query = Task.query
    return jsonify(paginate(tasks_query, page, per_page))


# Route to update a task
@app.route('/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    """
    Update a task by ID
    ---
    tags:
      - Tasks
    parameters:
      - name: task_id
        in: path
        type: string
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            title:
              type: string
            description:
              type: string
    responses:
      200:
        description: Task updated successfully
      404:
        description: Task not found
      400:
        description: Invalid input
    """
    task = Task.query.get(task_id)
    if task is None:
        abort(404)

    if not request.json:
        abort(400)

    task.title = request.json.get('title', task.title)
    task.description = request.json.get('description', task.description)

    db.session.commit()
    return jsonify(task.to_dict())

# Route to delete a task
@app.route('/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    """
    Delete a task by ID
    ---
    tags:
      - Tasks
    parameters:
      - name: task_id
        in: path
        type: string
        required: true
    responses:
      204:
        description: Task deleted successfully
      404:
        description: Task not found
    """
    task = Task.query.get(task_id)
    if task is None:
        abort(404)

    db.session.delete(task)
    db.session.commit()
    return '', 204

# Initialize the database and run the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables if not exists
    app.run(debug=True)
