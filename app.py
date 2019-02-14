#Skin Cancer Model Version 1.0.3
import os
from flask import Flask, request, jsonify, render_template, url_for
from werkzeug.utils import secure_filename
import numpy as np
import keras
from keras.preprocessing import image
from keras import backend as K
# please keep this import below. needed for db connection
from flask_sqlalchemy import SQLAlchemy

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

application = Flask(__name__)
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# please do not remove. connection to aws database instance
# # application.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://meghana95:awsMySQLmeg95@aaeybycoop6ulm.cfsmu6vnshf2.us-east-2.rds.amazonaws.com:3306/aaeybycoop6ulm'
# db = SQLAlchemy(application)

model = None
graph = None


def load_model():
    global model
    global graph
    model = keras.models.load_model('static/models/sugimachine.h5')
    graph = K.get_session().graph


def predict(image_path):
    K.clear_session()
    model = keras.models.load_model('static/models/sugimachine.h5')
    print()
    image_size = (200, 200)
    img = image.load_img(image_path, target_size=image_size)
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    predictions = list(model.predict(x)[0])
    return predictions

def two_max(list):
    if list[1]>list[0]:
        max_1=1
        max_2=0
    else:
        max_1=1
        max_2=0

    for i in range(2,18):
        if list[i] > list[max_1]:
            max_2 = max_1
            max_1 = i
        elif list[i] > list[max_2]:
            max_2=i

    return max_1, max_2



types = ['Bug', 'Dark', 'Dragon', 'Electric', 'Fairy', 'Fighting', 'Fire', 'Flying', 'Ghost', 'Grass', 'Ground', 'Ice', 'Normal', 'Poison', 'Psychic', 'Rock', 'Steel', 'Water']


def predicttypes(predictions):
    """Read in list of confidence and return tuple of two types predicted"""
    i_1, i_2 = two_max(predictions)
    type_1 = types[i_1]
    type_2 = types[i_2]
    return type_1, type_2


@application.route('/', methods=['GET', 'POST'])
def upload_file():
    data = {"success": False}
    type_1 = None
    type_2 = None
    info = print(url_for('upload_file'))

    if request.method == 'POST':
        print(request)

        if request.files.get('file'):
            file = request.files['file']
            pokename = request.form['pokename'].title()

            filename = file.filename

            filepath = os.path.join(application.config['UPLOAD_FOLDER'], filename)

            file.save(filepath)

            image_size = (200, 200)
            predictions = predict(filepath)
            # jsonify([int(p) for p in predictions])
            # results = [int(p) for p in predictions]

            rel_filepath=f"/static/uploads/{filename}"

            type_1, type_2 = predicttypes(predictions)

            return render_template("home.html", vis_1="hidden", vis_2="", type_1=type_1, type_2=type_2, wtp=f"It's {pokename}!", wtp_img=rel_filepath)

    return render_template("home.html", vis_1="", vis_2="hidden", type_1=type_1, type_2=type_2, wtp="Who's That Pokémon?", wtp_img="/static/images/wtp.png")



@application.route('/analysis')
def analysis():
    return render_template("analysis.html")

if __name__ == '__main__':
    application.run(debug=True)
