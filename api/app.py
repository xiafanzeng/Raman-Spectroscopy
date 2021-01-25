import json, time 
from flask import Flask, request, jsonify
from flask_api import status
import os
from pathlib import Path

app = Flask(__name__)

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
@app.route('/sepctrums', methods=['GET'])
def get_all_sepctrums():
    # select all
    # data_dir = Path('./data')
    # for filename in data_dir.iter():
    #     s = read_spectrum(filename, database_name)
    
    return 'all spectrums'

@app.route('/sepctrum/<id>', methods=['GET'])
def get_one_sepctrum(id):
    # selcet * from raman where id={id}
    
    return f'spectrum {id}'

@app.route('/sepctrum/query', methods=['GET'])
def query_spectrums():
    # options to query
    if not request.args: return f'empty opts'
    all_opts = {'num_page', 'total'} # ... 
    opts = all_opts and request.args
    
    if not opts: return f'Invalid query opts'
    
    args = {}
    for opt in opts:
        args[opt] = request.args[opt]
    
    # return query_funciton(*args)
    return f'query {args}' 

@app.route('/sepctrum/<id>', methods=['POST'])
def create_one_spectrum():
    # delete operation
    
    return f'created'

@app.route('/sepctrum/<id>', methods=['DELETE'])
def delete_one_spectrum():
    # create operation
    
    return f'deleted'


if __name__ == '__main__':
    app.run(host='0.0.0.0')