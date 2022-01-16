import os
import json
from flask import Flask, flash, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from os.path import join, dirname, realpath
UPLOAD_FOLDER = join(dirname(realpath(__file__)), 'static/uploads/')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        seed = request.form.get('seed')
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename_image = secure_filename(seed)+'.png'
            filename_json = secure_filename(seed)+'.json'
            filename_base = "base.json"
            with open(filename_base,'r') as f:
                data=json.load(f)
                data["properties"]["files"][0]["uri"] = "http://newtfrogtoad.tech:5000"+url_for('download_file', name=filename_image)
                data["image"] = "http://newtfrogtoad.tech:5000"+url_for('download_file', name=filename_image)
            basedir = os.path.abspath(os.path.dirname(__file__))
            with open(os.path.join(basedir, app.config['UPLOAD_FOLDER'], filename_json),'w') as f:
                json.dump(data,f,indent=4)
            file.save(os.path.join(basedir, app.config['UPLOAD_FOLDER'], filename_image))
            os.system(f"python3.9 metaplex/python-api/test_api.py --url_json 'http://newtfrogtoad.tech:5000/uploads/{filename_json}'")
            return redirect(url_for('download_file', name=filename_json))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=text name=seed>
      <input type=submit value=Upload>
    </form>
    '''

@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)
