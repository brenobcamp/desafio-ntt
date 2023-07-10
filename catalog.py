from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from flask import (Blueprint, render_template, session, 
                    request, url_for, jsonify, 
                    make_response, redirect, abort,
                    flash)
from bson import json_util
from werkzeug.utils import secure_filename
import json
import os
from http import HTTPStatus


bp = Blueprint('catalog', __name__)
# app = Flask(__name__)
uri = "mongodb+srv://brenocampos:sapoazul@clusterazure.tybruw9.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client.urls
collection = db.urls

@bp.route("/index")
def index():
    return render_template("home.html")

@bp.route("/")
def home():
    return render_template("listagem.html")

@bp.route("/cadastro")
def cadastro():
    return render_template("cadastro.html")

@bp.route("/remocao")
def remocao():
    return render_template("remocao.html")

@bp.route("/get", methods=['GET'])
def get():
    find = collection.find()
    list_cur = list(find)
    json = json_util.dumps(list_cur)
    return json


@bp.route("/post", methods=['GET', 'POST'])
def post():
    if request.method == 'POST':
        file = request.files['file']
        full_name = request.form['nome'] + secure_filename(file.filename)
        file.save('/workspace/desafiontt/static/user_files/' + full_name)

        post = {
            'nome': request.form['nome'].strip(),
            'especie': request.form['especie'].strip(),
            'ordem': request.form['ordem'].strip(),
            'imagem': 'https://5000-brenobcamp-desafiontt-rnqu8sqh0c8.ws-us101.gitpod.io/static/user_files/' + full_name
        }
        collection.insert_one(post)
        flash('Registro criado')
        return redirect(url_for('catalog.home'))


@bp.route("/delete", methods=['POST', 'DELETE'])
def delete():
    if request.method == 'POST':
        if collection.find_one({"nome": request.form['delete']}):
            delete = collection.find_one({"nome": request.form['delete']})
            file = delete['imagem'].split("https://5000-brenobcamp-desafiontt-rnqu8sqh0c8.ws-us101.gitpod.io/static/user_files/")
            file = file[1]
            os.remove(f'/workspace/desafiontt/static/user_files/{file}')
            collection.delete_one({'nome': request.form['delete']})
            flash('Registro criado')
            return redirect(url_for('catalog.home'))
    if request.method == 'DELETE':
        req_data = request.json
        delete = collection.find_one(req_data)
        file = delete['imagem'].split("https://5000-brenobcamp-desafiontt-rnqu8sqh0c8.ws-us101.gitpod.io/static/user_files/")
        file = file[1]
        os.remove(f'/workspace/desafiontt/static/user_files/{file}')
        collection.delete_one(req_data)
        return jsonify({'code': HTTPStatus.OK, 
                        'message': 'Deleted'})
    return abort(404)


@bp.route('/create',methods=['POST'])
def create():
    req_data = request.json
    collection.insert_one(req_data)
    return jsonify({'code': HTTPStatus.OK, 
                    'message': 'Created'})


@bp.route("/update/<string:code>", methods=['PUT'])
def put(code, url, image):
    collection.update_one({'code': code, 'url': url, 'image': image})
    return 'Updated', 200

@bp.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404