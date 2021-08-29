

"""Application routes."""
# from operator import itemgetter
# import pyecharts.options as opts
# from pyecharts.charts import Line
# import demjson
# from datetime import datetime as dt
# import pandas as pd
# import numpy as np
# import json
# import flask
# from flask import current_app as app
# from flask import make_response, redirect, render_template, request, url_for, jsonify, \
#     send_from_directory
# from flask_api import status
#
# from ..models import User, db, Spectrum
# # from ..templates
# from ..classification import random_forest, boosting, feat_peak, siamese

from operator import itemgetter
import pyecharts.options as opts
from pyecharts.charts import Line
import demjson
from datetime import datetime as dt
import pandas as pd
import numpy as np
import json
import flask
from flask import current_app as app
from flask import make_response, redirect, render_template, request, url_for, jsonify, \
    send_from_directory, Response
from flask_api import status

from app.models import User, db, Spectrum

from app.classification import random_forest, boosting, feat_peak, siamese



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

@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

# apis
@app.route('/', methods=['GET'])
def index():
    return send_from_directory('templates', 'Bootstrap-raman-index.html')


@app.route('/spectrum', methods=['POST'])
def create_one_spectrum():
    # create operation
    req = request.get_json()
    name, data ,cas= itemgetter('name', 'data','cas')(req)
    print(name)
    print(data)
    if 'x' in data and 'y' in data and data['x'] and data['y']:
        existing_spectrum = Spectrum.query.filter(
            Spectrum.data == f'{data}'
            # Spectrum.name == name
        ).first()
        if existing_spectrum: return make_response(f"{name} already created!")
        new_spectrum = Spectrum(
            name=name,
            created=dt.now(),
            data=f'{data}',
            cas=cas
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



@app.route('/check.html', methods=['GET'])
def return_index_html():
    return send_from_directory('static', 'check.html')


@app.route('/spectrum/check.html', methods=['GET'])
def return_check_html():
    return send_from_directory('static', 'check.html')


@app.route('/spectrum/downloadfile', methods=['GET'])
def return_down_txt():
    # filename = 'raman.txt'

    # 普通下载
    # response = make_response(send_from_directory(filepath, filename, as_attachment=True))
    # response.headers["Content-Disposition"] = "attachment; filename={}".format(filepath.encode().decode('latin-1'))
    # return send_from_directory(filepath, filename, as_attachment=True)
    # 流式读取
    def send_file():
        store_path = 'app/templates/raman.txt'
        with open(store_path, 'rb') as targetfile:
            while 1:
                data = targetfile.read(20 * 1024 * 1024)  # 每次读取20M
                if not data:
                    break
                yield data

    response = Response(send_file(), content_type='application/octet-stream')
    response.headers[
        "Content-disposition"] = 'attachment; filename=%s' % 'raman.txt'  # 如果不加上这行代码，导致下图的问题
    return response
    # return send_from_directory('public', 'raman.txt', as_attachment=True)

@app.route('/spectrum/query', methods=['POST'])
def query_spectrums():
    query_sort = flask.request.form.get('query_sort')
    query_number = flask.request.form.get('query_number')

    print(query_sort)
    print(query_number)

    if query_sort == 'id':
        raman_id = query_number
        exist_spectrum = Spectrum.query.get(raman_id)

        if exist_spectrum:
            b = demjson.decode(exist_spectrum.data)
            x = b['x']
            y = b['y']

            result = {'name': exist_spectrum.name, 'cas': exist_spectrum.cas,
                      'id': exist_spectrum.id,
                      'Raman_shift': 'Intensity'}

            file = open('app/templates/raman.txt', 'w')
            for k, v in result.items():
                file.write(str(k) + ' ' + str(v) + '\n')

            for i, j in zip(x, y):
                file.write(str(i) + ' ' + str(j) + '\n')

            file.close()
            print(result)
            print(x)
            print(y)
            print(exist_spectrum.name)
            c = (
                Line().add_xaxis(x)
                    .add_yaxis('', y)
                    .set_global_opts(
                    title_opts=opts.TitleOpts(title=exist_spectrum.name)))
            c.render(path='app/static/check.html')
            return send_from_directory('static', 'query.html')
        else:
            return '光谱不存在'

    elif query_sort == 'CAS':

        raman_cas = query_number
        try:
            exist_spectrum = Spectrum.query.filter_by(CAS=raman_cas).all()[0]

            if exist_spectrum:
                b = demjson.decode(exist_spectrum.data)

                x = b['x']
                y = b['y']
                result = {'name': exist_spectrum.name, 'cas': exist_spectrum.cas,
                          'id': exist_spectrum.id,
                          'Raman_shift': 'Intensity'}

                file = open('app/templates/raman.txt', 'w')
                for k, v in result.items():
                    file.write(str(k) + ' ' + str(v) + '\n')

                for i, j in zip(x, y):
                    file.write(str(i) + ' ' + str(j) + '\n')

                file.close()
                print(x)
                print(y)
                print(exist_spectrum.name)
                c = (
                    Line().add_xaxis(x)
                        .add_yaxis('', y)
                        .set_global_opts(
                        title_opts=opts.TitleOpts(title=exist_spectrum.name)))
                c.render(path='app/static/check.html')
                return send_from_directory('static', 'query.html')
        except:
            return '光谱不存在'

    elif query_sort == 'name':

        raman_name = query_number
        try:
            exist_spectrum = Spectrum.query.filter_by(name=raman_name).all()[0]
            print(exist_spectrum)
            if exist_spectrum:
                b = demjson.decode(exist_spectrum.data)

                x = b['x']
                y = b['y']

                result = {'name': exist_spectrum.name, 'cas': exist_spectrum.cas,
                          'id': exist_spectrum.id,
                          'Raman_shift': 'Intensity'}

                file = open('app/templates/raman.txt', 'w')
                for k, v in result.items():
                    file.write(str(k) + ' ' + str(v) + '\n')

                for i, j in zip(x, y):
                    file.write(str(i) + ' ' + str(j) + '\n')

                file.close()
                print(x)
                print(y)
                print(exist_spectrum.name)
                c = (
                    Line().add_xaxis(x)
                        .add_yaxis('', y)
                        .set_global_opts(
                        title_opts=opts.TitleOpts(title=exist_spectrum.name)))
                c.render(path='app/static/check.html')
                return send_from_directory('static', 'query.html')
        except:
            return '光谱不存在'
    else:
        return '参数有误，请重新输入'



@app.route('/spectrum', methods=['PUT'])
def update_one_spectrum():
    # update operation
    temp_id = 0
    file = open('app/templates/raman.txt')
    for line in file:
        line = line.strip("\n").split(" ")
        a,b=line[0],line[1]
        if (a!="id"):
            continue
        else:
            temp_id = int(b)
            break

    spectrum = request.get_json()
    name, cas, data = itemgetter('name', 'cas', 'data')(spectrum)

    exist_spectrum = Spectrum.query.get(temp_id)
    if exist_spectrum:
        exist_spectrum.name = name
        exist_spectrum.cas = cas
        exist_spectrum.data = f'{data}'
        db.session.commit()
        return jsonify(status=200, message='updated')
    else:
        return not_found('')


@app.route('/spectrum', methods=['DELETE'])
def delete_one_spectrum():
    # delete operation
    temp_id = 0
    file = open('app/templates/raman.txt')
    for line in file:
        line = line.strip("\n").split(" ")
        a,b=line[0],line[1]
        if (a!="id"):
            continue
        else:
            temp_id = int(b)
            break

    exist_spectrum = Spectrum.query.get(temp_id)
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
    # json数据解析转换格式xxxx  error
    sample = np.array(data['y'])[None, :]

    if method == 'rf':
        result = random_forest.rf_clf(sample, (X, Y))

    elif method == 'boosting':
        result = boosting.gbt_clf(sample, (X, Y))

    else:
        method_not_supported('')

    return jsonify(status=200, message=result)
