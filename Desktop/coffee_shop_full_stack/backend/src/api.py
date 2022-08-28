import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth, get_token_auth_header, verify_decode_jwt

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['GET'])
def getDrinks():

    try:
        drink = Drink.query.all()

        drinks = [drink.short() for drink in drink]

        return jsonify({"success": True, "drinks": drinks})
    except BaseException:
        abort(404)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def getDrinksDetails(payload):
    try:
        drink = Drink.query.all()

        drinks = [drink.long() for drink in drink]

        return jsonify({"success": True, "drinks": drinks})
    except BaseException:
        abort(404)


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(payload):

    new_drinks = request.get_json()
    try:
        title = new_drinks.get('title', None)
        recipe = json.dumps(new_drinks.get('recipe', None))
        drink = Drink(title=title, recipe=recipe)
        drink.insert()
        load_drink = drink.long()
        return jsonify({"success": True, "drinks": [load_drink]})

    except BaseException:
        abort(422)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patchDrinks(payload, id):

    try:
        new_drink = request.get_json()

        if ('title' in new_drink and 'recipe' in new_drink):
            title = new_drink['title']
            recipes = json.dumps(new_drink['recipe'])
            patch_drink = Drink.query.filter(Drink.id == id).first()

            patch_drink.title = title
            patch_drink.recipe = recipes

            patch_drink.update()
            drink = patch_drink.long()
            return jsonify({"success": True, "drinks": [drink]})
    except BaseException:
        abort(422)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def deleteDrinks(payload, id):

    try:
        # drink = Drink.query.filter_by(id==id).first()
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        drink.delete()

        return jsonify({"success": True, "delete": id})
    except BaseException:
        abort(422)


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


@app.errorhandler(404)
def not_found(error):

    return jsonify({
        'success': False,
        'error': 404,
        'message': 'resource not found'
    }), 404


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''

@app.errorhandler(AuthError)
def handle_auth_error(ex):
    """
    Receive the raised authorization error and propagates it as response
    """
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response

@app.errorhandler(401)
def unauthorised(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Unauthorized"
    }), 401


@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal Server Error"
    }), 500


@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "forbidden access"
    }), 403


@app.errorhandler(400)
def forbidden(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Invalid Header"
    }), 400


@app.errorhandler(405)
def forbidden(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "Method Not Allowed"
    }), 405
