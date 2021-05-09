from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import pickle
model = pickle.load(open('model', 'rb'))
COLUMNS_ORDER = ['age', 'sex', 'trestbps', 'chol', 'fbs', 'thalach', 'exang', 'oldpeak',
       'cp_1', 'cp_2', 'cp_3', 'restecg_1', 'restecg_2', 'slope_1',
       'slope_2', 'ca_1', 'ca_2', 'ca_3', 'ca_4', 'thal_1', 'thal_2',
       'thal_3']

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

class Recording(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.Integer, nullable=False)
    sex = db.Column(db.Integer, nullable=False)
    trestbps = db.Column(db.Integer, nullable=False)
    chol = db.Column(db.Integer, nullable=False)
    fbs = db.Column(db.Integer, nullable=False)
    thalach = db.Column(db.Integer, nullable=False)
    exang = db.Column(db.Integer, nullable=False)
    oldpeak = db.Column(db.Float, nullable=False)
    cp_1 = db.Column(db.Integer, nullable=False)
    cp_2 = db.Column(db.Integer, nullable=False)
    cp_3 = db.Column(db.Integer, nullable=False)
    restecg_1 = db.Column(db.Integer, nullable=False)
    restecg_2 = db.Column(db.Integer, nullable=False)
    slope_1 = db.Column(db.Integer, nullable=False)
    slope_2 = db.Column(db.Integer, nullable=False)
    ca_1 = db.Column(db.Integer, nullable=False)
    ca_2 = db.Column(db.Integer, nullable=False)
    ca_3 = db.Column(db.Integer, nullable=False)
    ca_4 = db.Column(db.Integer, nullable=False)
    thal_1 = db.Column(db.Integer, nullable=False)
    thal_2 = db.Column(db.Integer, nullable=False)
    thal_3 = db.Column(db.Integer, nullable=False)
    target = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return str(self.id)
@app.route('/')
def index():
    return "hello world"

@app.route('/page')
def page():
    return "page"

@app.route('/test')
def test():
    return {"key" : 'passed'}

@app.route('/get-prediction', methods=['GET', 'POST'])
def predict():
    # Getting the data sent to the API
    data = request.json
    # Setting the the categorical values and their possible values
    categorical_values = {'cp' : [1, 2, 3],
                          'restecg' : [1, 2],
                          'slope' : [1, 2],
                          'ca' : [1, 2, 3, 4],
                          'thal' : [1, 2, 3]}
    # Adding the dummy variables
    for value in categorical_values:
        for val in categorical_values[value]:
            if val == data[value]:
                data[value + '_' + str(val)] = 1
            else:
                data[value + '_' + str(val)] = 0
        del data[value]
    # Preparing the data for the model
    to_model = [data[col] for col in COLUMNS_ORDER]
    # Making the prediction76t
    pred = model.predict([to_model])
    # Preparing the response
    response = {"pred" : int(pred[0])}
    r = Recording(age=data['age'], sex=data['sex'], trestbps=data['trestbps'],
                  chol=data['chol'], fbs=data['fbs'], thalach=data['thalach'],
                  exang=data['exang'], oldpeak=data['oldpeak'], cp_1=data['cp_1'],
                  cp_2=data['cp_2'], cp_3=data['cp_3'], restecg_1=data['restecg_1'],
                  restecg_2=data['restecg_2'], slope_1=data['restecg_1'],
                  slope_2=data['slope_2'], ca_1=data['ca_1'], ca_2=data['ca_2'],
                  ca_3=data['ca_3'], ca_4=data['ca_4'], thal_1=data['thal_1'],
                  thal_2=data['thal_2'], thal_3=data['thal_3'], target=response['pred'])
    try:
        db.session.add(r)
        db.session.commit()
    except:
        return "An Error ocured during the storing of the data."
    return jsonify(response)

if __name__ == '__main__':
    app.run()