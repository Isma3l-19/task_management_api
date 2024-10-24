# app.py
from flask import Flask, jsonify, request, abort
from flasgger import Swagger
import uuid

app = Flask(__name__)
swagger = Swagger(app)

# In-memory task store (acts like a database for now)
tasks = []

# Helper function to find task by ID
def find_task(task_id):
    return next((task for task in tasks if task['id'] == task_id), None)

# Swagger UI configuration
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

    task = {
        'id': str(uuid.uuid4()),
        'title': request.json['title'],
        'description': request.json.get('description', "")
    }
    tasks.append(task)
    return jsonify(task), 201

@app.route('/tasks', methods=['GET'])
def get_tasks():
    """
    Get the list of all tasks
    ---
    tags:
      - Tasks
    responses:
      200:
        description: A list of tasks
        schema:
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
    return jsonify(tasks)

@app.route('/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    """
    Get a specific task by ID
    ---
    tags:
      - Tasks
    parameters:
      - name: task_id
        in: path
        type: string
        required: true
        description: The ID of the task to retrieve
    responses:
      200:
        description: A task object
        schema:
          type: object
          properties:
            id:
              type: string
            title:
              type: string
            description:
              type: string
      404:
        description: Task not found
    """
    task = find_task(task_id)
    if task is None:
        abort(404)
    return jsonify(task)

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
    task = find_task(task_id)
    if task is None:
        abort(404)

    if not request.json:
        abort(400)

    task['title'] = request.json.get('title', task['title'])
    task['description'] = request.json.get('description', task['description'])

    return jsonify(task)

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
    task = find_task(task_id)
    if task is None:
        abort(404)

    tasks.remove(task)
    return '', 204

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
