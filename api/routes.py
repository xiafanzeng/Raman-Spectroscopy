"""Application routes."""
from operator import itemgetter
from datetime import datetime as dt
import pandas as pd
import numpy as np
import json

from flask import current_app as app
from flask import make_response, redirect, render_template, request, url_for, jsonify, \
    send_from_directory
from flask_api import status

from .models import User, db, Spectrum

from .classification import random_forest, boosting, feat_peak, siamese


@app.route("/user", methods=["GET"])
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
@app.route('/', methods=['GET'])
def index():
    return send_from_directory('public', 'index.html')


@app.route('/spectrum', methods=['POST'])
def create_one_spectrum():
    # create operation
    req = request.get_json()
    name, data = itemgetter('name', 'data')(req)
    print(name)
    if 'x' in data and 'y' in data and data['x'] and data['y']:
        existing_spectrum = Spectrum.query.filter(
            Spectrum.data == f'{data}'
            # Spectrum.name == name
        ).first()
        if existing_spectrum: return make_response(f"{name} already created!")
        new_spectrum = Spectrum(
            name=name,
            created=dt.now(),
            data=f'{data}'
            # **req
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
        # print(type(spectrums[i]))
        spectrums[i] = spectrum.__repr__()
        # print(type(spectrums[i]))
    return jsonify(status=200, message=json.dumps(spectrums))
    # return 'all spectrums'


@app.route('/spectrum/<id>', methods=['GET'])
def get_one_spectrum(id):
    # selcet * from raman where id={id}
    exist_spectrum = Spectrum.query.get(id)
    if exist_spectrum:
        return jsonify(status=200, message=exist_spectrum.__repr__())
    else:
        return not_found('')


@app.route('/spectrum/query', methods=['GET'])
def query_spectrums():
    # options to query
    if not request.args: return bad_request('no query exist')

    # arg set
    exist_spectrums = set()
    for key in request.args.keys():
        exist_spectrum = Spectrum.query.filter(
            getattr(Spectrum, key) == request.args[key]
        ).all()
        for spectrum in exist_spectrum: exist_spectrums.add(spectrum)

    if len(exist_spectrums):
        return jsonify(status=200, message=exist_spectrums.__repr__())
    else:
        return not_found('')


# from sqlalchemy.orm import sessionmaker
# Session = sessionmaker(Spectrum)
# db_session = Session()

@app.route('/spectrum/<id>', methods=['PUT'])
def update_one_spectrum(id):
    # update operation
    spectrum = request.get_json()
    name, cas, data = itemgetter('name', 'cas', 'data')(spectrum)

    exist_spectrum = Spectrum.query.get(id)
    # print(exist_spectrum)
    # res = db_session.query(Spectrum).filter().update({"data": data})
    if exist_spectrum:
        exist_spectrum.name = name
        exist_spectrum.cas = cas
        exist_spectrum.data = f'{data}'
        db.session.commit()
        return jsonify(status=200, message='updated')
    else:
        return not_found('')


@app.route('/spectrum/<id>', methods=['DELETE'])
def delete_one_spectrum(id):
    # delete operation
    exist_spectrum = Spectrum.query.get(id)
    if exist_spectrum:
        db.session.delete(exist_spectrum)
        db.session.commit()
        return jsonify(status=200, message='deleted')
    else:
        return not_found('')


@app.route('/spectrum/classification', methods=['POST'])
def classify_spectrum():
    spectrum = request.get_json()

    # unknow
    data = f'{itemgetter("data")(spectrum)}'
    method = ''
    if 'method' in spectrum: method = spectrum['method']

    # known
    spectrums = Spectrum.query.all()

    # 默认方法
    if not method or method == '':
        all_spectrums = {}
        for s in spectrums:
            _s = json.loads(s.data.replace("'", '"'))
            all_spectrums[s.name] = [_s['x'], _s['y']]
        result = feat_peak.classify(data['x'], data['y'], all_spectrums)

    # load known spectrum data
    X, Y = [], []
    for s in spectrums:
        _s = json.loads(s.data.replace("'", '"'))
        X.append(_s['y'])
        Y.append(s.name)
    X = pd.DataFrame(X)
    sample = np.array(data['y'])[None, :]

    if method == 'rf':
        result = random_forest.rf_clf(sample, (X, Y))

    elif method == 'boosting':
        result = boosting.gbt_clf(sample, (X, Y))

    else:
        method_not_supported('')

    return jsonify(status=200, message=result)
