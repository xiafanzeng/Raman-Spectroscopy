"""Application routes."""
from operator import itemgetter
from datetime import datetime as dt

import json

from flask import current_app as app
from flask import make_response, redirect, render_template, request, url_for, jsonify
from flask_api import status

from .models import User, db, Spectrum


@app.route("/", methods=["GET"])
def user_records():
    """Create a user via query string parameters."""
    username = request.args.get("user")
    email = request.args.get("email")
    if username and email:
        existing_user = User.query.filter(
            User.username == username or User.email == email
        ).first()
        if existing_user:
            return make_response(f"{username} ({email}) already created!")
        new_user = User(
            username=username,
            email=email,
            created=dt.now(),
            bio="In West Philadelphia born and raised, \
            on the playground is where I spent most of my days",
            admin=False,
        )  # Create an instance of the User class
        db.session.add(new_user)  # Adds new User record to database
        db.session.commit()  # Commits all changes
        redirect(url_for("user_records"))
    return render_template("users.jinja2", users=User.query.all(), title="Show Users")


# exceptions
@app.errorhandler(Exception)
def request_validation_error(error):
    """ Handles Value Errors from bad data """
    return bad_request(error)

@app.errorhandler(status.HTTP_400_BAD_REQUEST)
def bad_request(error):
    """ Handles bad reuests with 400_BAD_REQUEST """
    message = str(error)
    app.logger.warning(message)
    return (
        jsonify(
            status=status.HTTP_400_BAD_REQUEST, error="Bad Request", message=message
        ),
        status.HTTP_400_BAD_REQUEST,
    )
    
@app.errorhandler(status.HTTP_404_NOT_FOUND)
def not_found(error):
    """ Handles resources not found with 404_NOT_FOUND """
    message = str(error)
    app.logger.warning(message)
    return (
        jsonify(status=status.HTTP_404_NOT_FOUND, error="Not Found", message=message),
        status.HTTP_404_NOT_FOUND,
    )
    
@app.errorhandler(status.HTTP_405_METHOD_NOT_ALLOWED)
def method_not_supported(error):
    """ Handles unsuppoted HTTP methods with 405_METHOD_NOT_SUPPORTED """
    message = str(error)
    app.logger.warning(message)
    return (
        jsonify(
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
            error="Method not Allowed",
            message=message,
        ),
        status.HTTP_405_METHOD_NOT_ALLOWED,
    )
    
@app.errorhandler(status.HTTP_500_INTERNAL_SERVER_ERROR)
def internal_server_error(error):
    """ Handles unexpected server error with 500_SERVER_ERROR """
    message = str(error)
    app.logger.error(message)
    return (
        jsonify(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error="Internal Server Error",
            message=message,
        ),
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    )    


# apis
@app.route('/spectrum', methods=['POST'])
def create_one_spectrum():
    # create operation
    req = request.get_json()
    name, cas, data = itemgetter('name', 'cas', 'data')(req)
    
    if 'x' in data and 'y' in data and data['x'] and data['y']:
        existing_spectrum = Spectrum.query.filter(
            Spectrum.data == data 
        ).first()
        if existing_spectrum: return make_response(f"{name} ({cas}) already created!")
        new_spectrum = Spectrum(
            name=name,
            cas=cas,
            created=dt.now(),
            data=data,
        )
        db.session.add(new_spectrum)
        db.session.commit()
        return jsonify(status=201, message='created')
    return bad_request('')

@app.route('/spectrums', methods=['GET'])
def get_all_spectrums():
    # select all
    spectrums = Spectrum.query.all()
    for i, spectrum in enumerate(spectrums):
        print(type(spectrums[i]))
        spectrums[i] = spectrum.__repr__()
        print(type(spectrums[i]))
    return jsonify(status=200, message=json.dumps(spectrums))
    # return 'all spectrums'

# uuid
@app.route('/spectrum/<id>', methods=['GET'])
def get_one_spectrum(id):
    # selcet * from raman where id={id}
    exist_spectrum = Spectrum.query.get(id)
    if exist_spectrum:
        return jsonify(status=200, message=exist_spectrum.__repr__())
    else: return not_found('')

# name cas
@app.route('/spectrum/query', methods=['GET'])
def query_spectrums():
    # options to query
    if not request.args: return f'empty opts'
    all_opts = {'num_page', 'total'} # ... 
    opts = all_opts and request.args
    
    if not opts: return f'Invalid query opts'
    
    args = {}
    for opt in opts:
        args[opt] = request.args[opt]

    return f'query {args}' 

@app.route('/spectrum/<id>', methods=['PUT'])
def update_one_spectrum(id):
    # update operation
    spectrum = request.get_json()
    name, cas, data = itemgetter('name', 'cas', 'data')(spectrum)

    exist_spectrum = Spectrum.query.get(id)
    if exist_spectrum: 
        exist_spectrum.name = name 
        exist_spectrum.cas = cas 
        exist_spectrum.data = data 
        db.session.commit()
        return jsonify(status=200, message='updated')
    else: not_found('')

@app.route('/spectrum/<id>', methods=['DELETE'])
def delete_one_spectrum(id):
    # delete operation
    exist_spectrum = Spectrum.query.get(id)
    if exist_spectrum: 
        db.session.delete(exist_spectrum)
        db.session.commit()
        return jsonify(status=200, message='deleted')
    else: return not_found('')

@app.route('/spectrum/classification', methods=['POST'])
def classify_spectrum():
    spectrum = request.get_json()
    data = itemgetter('data')(spectrum)
    return ''
    
