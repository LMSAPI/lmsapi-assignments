from flask import Flask, request, abort
from flask_pymongo import PyMongo
from functools import wraps
from bson import json_util

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'heroku_k0kdm9jl'
app.config['MONGO_URI'] = 'mongodb://test_user:test_pass@ds157380.mlab.com:57380/heroku_k0kdm9jl'
app.secret_key = 'mysecret'

mongo = PyMongo(app)


def require_appkey(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        if request.args.get('key') and key_exists(request.args.get('key')):
            return view_function(*args, **kwargs)
        else:
            abort(401)

    return decorated_function


@app.route('/')
@require_appkey
def root():
    return 'hello there'


@app.route('/assignments/<course>/<assignment>', methods=['POST', 'GET', 'PUT', 'DELETE'])
@require_appkey
def student_assignments(course, assignment):
    mongo_student_assignments = mongo.db.student_assignments
    teacheruser = user_name(request.args.get('key'))

    # get all students in assignment
    if request.method == 'GET':
        assignments_resp = mongo_student_assignments.find({'number': assignment,
                                                           'course_num': course,
                                                           'teacheruser': teacheruser})
        return json_util.dumps(assignments_resp)

    # insert new student into assignment
    if request.method == 'POST':
        existing_assignment = mongo_student_assignments.find_one({'number': assignment,
                                                                  'course_num': course,
                                                                  'email': request.args.get('email'),
                                                                  'teacheruser': teacheruser})
        if existing_assignment is None:
            mongo_student_assignments.insert({'number': assignment,
                                              'course_num': course,
                                              'email': request.args.get('email'),
                                              'grade': request.args.get('grade'),
                                              'teacheruser': teacheruser})
            return 'Added'

        return 'already exists!'

    # update a student in a assignment
    if request.method == 'PUT':
        existing_assignment = mongo_student_assignments.find_one({'number': assignment,
                                                                  'course_num': course,
                                                                  'email': request.args.get('email'),
                                                                  'teacheruser': teacheruser})
        if existing_assignment is not None:
            print(request.args)
            mongo_student_assignments.update_one({'number': assignment,
                                                  'course_num': course,
                                                  'email': request.args.get('email'),
                                                  'teacheruser': teacheruser},
                                                 {'$set': {'grade': request.args.get('grade')}})
            return 'Updated'

        return 'Update failed'

    # delete a student from a assignment
    if request.method == 'DELETE':
        existing_assignment = mongo_student_assignments.find_one({'number': assignment,
                                                                  'course_num': course,
                                                                  'email': request.args.get('email'),
                                                                  'teacheruser': teacheruser})
        if existing_assignment is not None:
            mongo_student_assignments.delete_one({'number': assignment,
                                                  'course_num': course,
                                                  'email': request.args.get('email'),
                                                  'teacheruser': teacheruser})
            return 'Deleted'

        return 'Delete failed'


@app.route('/assignments', methods=['POST'], defaults={'course': None})
@app.route('/assignments/<course>', methods=['GET', 'PUT', 'DELETE'])
@require_appkey
def assignments(course):
    mongo_assignments = mongo.db.assignments
    teacheruser = user_name(request.args.get('key'))

    # get all assignments
    if request.method == 'GET':
        assignments_resp = mongo_assignments.find({'course_num': course,
                                                   'teacheruser': teacheruser})
        return json_util.dumps(assignments_resp)

    # insert new assignment
    if request.method == 'POST':
        existing_assignment = mongo_assignments.find_one({'number': request.args.get('number'),
                                                          'course_num': request.args.get('course_num'),
                                                          'teacheruser': teacheruser})
        if existing_assignment is None:
            mongo_assignments.insert({'number': request.args.get('number'),
                                      'course_num': request.args.get('course_num'),
                                      'name': request.args.get('name'),
                                      'type': request.args.get('type'),
                                      'due': request.args.get('due'),
                                      'teacheruser': teacheruser})
            return 'Added'

        return 'already exists!'

    # update a assignment
    if request.method == 'PUT':
        existing_assignment = mongo_assignments.find_one({'number': request.args.get('number'),
                                                          'course_num': course,
                                                          'teacheruser': teacheruser})
        if existing_assignment is not None:
            print(request.args)
            mongo_assignments.update_one({'number': assignment,
                                          'course_num': course,
                                          'teacheruser': teacheruser},
                                         {'$set': {'name': request.args.get('name'),
                                                   'type': request.args.get('type'),
                                                   'due': request.args.get('due')}})
            return 'Updated'

        return 'Update failed'

    # delete a assignment
    if request.method == 'DELETE':
        existing_assignment = mongo_assignments.find_one({'number': request.args.get('number'),
                                                          'course_num': course,
                                                          'teacheruser': teacheruser})
        if existing_assignment is not None:
            mongo_assignments.delete_one({'number': request.args.get('number'),
                                          'course_num': course,
                                          'teacheruser': teacheruser})
            return 'Deleted'

        return 'Delete failed'


def obj_dict(obj):
    return obj.__dict__


def user_name(key):
    users = mongo.db.users
    user = users.find_one({'apikey': key})
    return user['name']


def key_exists(key):
    users = mongo.db.users
    user_key = users.find_one({'apikey':key})

    if user_key is None:
        return False

    return True


if __name__ == '__main__':
    app.run(debug=True)
