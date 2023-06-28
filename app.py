from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from flask import Flask, render_template, session, request, url_for, jsonify, make_response, redirect, abort
from bson import json_util
from werkzeug.utils import secure_filename
import json
import os

app = Flask(__name__)
uri = "mongodb+srv://brenocampos:sapoazul@clusterazure.tybruw9.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client.urls
collection = db.urls

@app.route("/")
def home():
    return render_template("home.html", documentos=collection.find())

@app.route("/post", methods=['GET', 'POST'])
def post():
    if request.method == 'POST':
        file = request.files['file']
        full_name = request.form['code'] + secure_filename(file.filename)
        file.save('/workspace/desafio-ntt/static/user_files/' + full_name)

        post = {
            'code': request.form['code'].strip(),
            'url': request.form['url'].strip(),
            'image': full_name
        }
        collection.insert_one(post)
        
        return "Created"

@app.route("/delete", methods=['POST', 'GET'])
def delete():
    if request.method == 'POST':
        if collection.find_one({"code": request.form['delete']}):
            delete = collection.find_one({"code": request.form['delete']})
            os.remove(f'/workspace/desafio-ntt/static/user_files/{delete["image"]}')
            collection.delete_one({'code': request.form['delete']})
            return "Deleted"

@app.route("/get", methods=['GET', 'POST'])
def get():
    find = collection.find()
    list_cur = list(find)
    json = json_util.dumps(list_cur)
    return json

@app.route("/<string:code>")
def redirect_to_url(code):
    if collection.find_one({"code": code}):
        document = collection.find_one({"code": code})
        return redirect(url_for('static', filename='user_files/' + document['image']))
    return abort(404)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404