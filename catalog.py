from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from flask import (Blueprint, render_template, session, request, 
                    url_for, jsonify, redirect, abort, flash)
from bson import json_util
from werkzeug.utils import secure_filename
from http import HTTPStatus
from random import choice
import json
import os


bp = Blueprint('catalog', __name__)
uri = "mongodb+srv://brenocampos:sapoazul@clusterazure.tybruw9.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client.insecta
collection = db.especies

# Web

@bp.route("/", methods=["GET"])
def home():
    imagens = []
    find = collection.find()
    for document in find:
        imagens.append(document['imagem'])
    return render_template("home.html", imagem=choice(imagens))


@bp.route("/lista", methods=['GET'])
def lista():
    documentos = collection.find()
    return render_template("lista.html", documentos=documentos)


@bp.route("/cadastro", methods=['GET'])
def cadastro():
    return render_template("cadastro.html")


@bp.route("/remocao", methods=['GET'])
def remocao():
    documentos = collection.find()
    return render_template("remocao.html", documentos=documentos)


@bp.route("/edicao/<string:nome>", methods=['GET'])
def edicao(nome):
    documento = collection.find_one({"nome": nome})
    return render_template("edicao.html", documentos=documento)


@bp.route("/about", methods=["GET"])
def about():
    return render_template("sobre.html")


@bp.route("/<string:code>")
def redirect_to(code):
    return abort(404)


@bp.errorhandler(404)
def page_not_found(error):
    return render_template('pagenotfound.html'), 404


# API

@bp.route("/get", methods=['GET'])
def get():
    find = collection.find()
    list_cur = list(find)
    json = json_util.dumps(list_cur)
    return json


@bp.route("/post", methods=['POST'])
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
    

@bp.route("/edicao/update", methods=["POST"])
def put():
    if request.method == 'POST':
        filtro = {"nome": request.form['nome_antigo']}

        if request.files['file']:
            delete = collection.find_one(filtro)
            imagem_antiga = delete['imagem'].split("https://5000-brenobcamp-desafiontt-rnqu8sqh0c8.ws-us101.gitpod.io/static/user_files/")
            imagem_antiga = imagem_antiga[1]
            os.remove(f'/workspace/desafiontt/static/user_files/{imagem_antiga}')

            imagem_nova = request.files['file']
            full_name = request.form['nome'] + secure_filename(imagem_nova.filename)
            imagem_nova.save('/workspace/desafiontt/static/user_files/' + full_name)

            atualizacao = { '$set': {
                'nome': request.form['nome'].strip(),
                'especie': request.form['especie'].strip(),
                'ordem': request.form['ordem'].strip(),
                'imagem': 'https://5000-brenobcamp-desafiontt-rnqu8sqh0c8.ws-us101.gitpod.io/static/user_files/' + full_name
            }
            }

            collection.update_one(filtro, atualizacao)
            flash('Registro editado')
            return redirect(url_for('catalog.home'))
        else:
            atualizacao = { '$set': {
                'nome': request.form['nome'].strip(),
                'especie': request.form['especie'].strip(),
                'ordem': request.form['ordem'].strip()
                }
            }

            collection.update_one(filtro, atualizacao)
            flash('Registro editado')
            return redirect(url_for('catalog.home'))
    return abort(404)


@bp.route('/create',methods=['POST'])
def create():
    req_data = request.json
    collection.insert_one(req_data)
    return jsonify({'code': HTTPStatus.OK, 
                    'message': 'Created'})


@bp.route('/update/<string:nome>', methods=['PUT'])
def update(nome):
    if request.method == 'PUT':
        filtro = {"nome": nome}
        req_data = request.json
        atualizacao = {"$set": req_data}
        result = collection.update_one(filtro, atualizacao)
        return jsonify({'code': HTTPStatus.OK, 
                        'message': 'Registro editado'})

    return abort(404)

            
@bp.route("/delete", methods=['POST', 'DELETE'])
def delete():
    if request.method == 'POST':
        if collection.find_one({"nome": request.form['delete']}):
            delete = collection.find_one({"nome": request.form['delete']})
            file = delete['imagem'].split("https://5000-brenobcamp-desafiontt-rnqu8sqh0c8.ws-us101.gitpod.io/static/user_files/")
            file = file[1]
            os.remove(f'/workspace/desafiontt/static/user_files/{file}')
            collection.delete_one({'nome': request.form['delete']})
            flash('Registro deletado')
            return redirect(url_for('catalog.remocao'))
    if request.method == 'DELETE':
        req_data = request.json
        delete = collection.find_one(req_data)
        file = delete['imagem'].split("https://5000-brenobcamp-desafiontt-rnqu8sqh0c8.ws-us101.gitpod.io/static/user_files/")
        file = file[1]
        os.remove(f'/workspace/desafiontt/static/user_files/{file}')
        collection.delete_one(req_data)
        return jsonify({'code': HTTPStatus.OK, 
                        'message': 'Registro deletado'})
    return abort(404)