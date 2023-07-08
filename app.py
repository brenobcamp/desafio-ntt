from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from flask import Flask, render_template, session, request, url_for, jsonify, make_response, redirect, abort
from bson import json_util
from werkzeug.utils import secure_filename
import json
import os
from http import HTTPStatus

app = Flask(__name__)
uri = "mongodb+srv://brenocampos:sapoazul@clusterazure.tybruw9.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client.urls
collection = db.urls


# Web

@app.route("/")
def home():
    return render_template("home.html", documentos=collection.find())


@app.route("/post", methods=['POST'])
def post():
    if request.method == 'POST':
        file = request.files['file']
        full_name = request.form['nome_cientifico'] + secure_filename(file.filename)
        file.save('/workspace/desafio-ntt/static/user_files/' + full_name)

        post = {
            'nome_comum': request.form['nome_comum'].strip(),
            'nome_cientifico': request.form['nome_cientifico'].strip(),
            'ordem': request.form['ordem'].strip(),
            'imagem': 'https://5000-brenobcamp-desafiontt-1j9w3kam4lw.ws-us101.gitpod.io/static/user_files/' + full_name
        }
        collection.insert_one(post)
        
        return "Created"


@app.route("/delete", methods=['POST', 'GET', 'DELETE'])
def delete():
    if request.method == 'POST':
        if collection.find_one({"nome_comum": request.form['delete']}):
            delete = collection.find_one({"nome_comum": request.form['delete']})
            file = delete['imagem'].split("https://5000-brenobcamp-desafiontt-1j9w3kam4lw.ws-us101.gitpod.io/static/user_files/")
            file = file[1]
            os.remove(f'/workspace/desafio-ntt/static/user_files/{file}')
            collection.delete_one({'nome_comum': request.form['delete']})
            return "Deleted"
    if request.method == 'DELETE':
        req_data = request.json
        delete = collection.find_one(req_data)
        file = delete['imagem'].split("https://5000-brenobcamp-desafiontt-1j9w3kam4lw.ws-us101.gitpod.io/static/user_files/")
        file = file[1]
        os.remove(f'/workspace/desafio-ntt/static/user_files/{file}')
        collection.delete_one(req_data)
        return "Deleted"
    return abort(404)

# API

@app.route("/get", methods=['GET'])
def get():
    find = collection.find()
    list_cur = list(find)
    json = json_util.dumps(list_cur)
    return json

@app.route('/create',methods=['POST'])
def createTask():
    req_data = request.json
    collection.insert_one(req_data)
    return 'Create new task'


@app.route("/update/<string:code>", methods=['PUT'])
def put(code, url, image):
    collection.update_one({'code': code, 'url': url, 'image': image})
    return 'Updated', 200


@app.route("/<string:code>")
def redirect_to_url(code):
    if collection.find_one({"code": code}):
        document = collection.find_one({"code": code})
        return redirect(url_for('static', filename='user_files/' + document['image']))
    return abort(404)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404