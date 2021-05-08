# Importing all needed libraries.
from flask import Flask, request, jsonify, render_template
import pickle
import numpy as np
import pandas as pd

def cosine_similarity(vec1, vec2):
    '''
        This function returns the cosine similarity of 2 vectors.
    :param vec1: np.array
        The first vector.
    :param vec2: np.array
        The second vector.
    :return: float
        The cosine similarity of the 2 vectors.
    '''
    # Getting the dot product of the 2 values.
    dot_product = np.dot(vec1, vec2.T)[0][0]

    # Getting the norm of every vector.
    norm1 = np.linalg.norm(vec1, ord=2)
    norm2 = np.linalg.norm(vec2, ord=2)

    # Computing and returning the cosine similarity.
    return dot_product / (norm1 * norm2)

def find_top_n(vec, matrix, n=5):
    '''
        This function returns the indexes of the most similar resumes.
    :param vec: np.array
        The vector representation of the query.
    :param matrix: sparse matrix
        The sparse matrix of the vectorised resumes.
    :param n: int
        The number results to return.
    :return: np.array
        The top n indexes with the most similar resumes.
    '''
    # Creating an empty list to store the cosine similarities.
    cos_sim = []

    # Computing the cosine similarity of every resume with the vector representation of the query.
    for i in range(len(matrix.toarray())):
        cos_sim.append(cosine_similarity(vec, matrix[i].toarray()))

    # Returning the n most similar indexes.
    return np.argsort(cos_sim)[-n:]

# Importing the names and skills from resumes data set.
df = pd.read_csv('db.csv')
X = df['skills'].values
names = df['names'].values

# Loading the vectorizer and generating the sparsed matrix.
vectorizer = pickle.load(open('vectorizer.obj', 'rb'))
X_sparse = vectorizer.transform(X)

# Creating the flask app.
app = Flask(__name__)

# Defining the main page functionality.
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        # Returning the template if the request is a GET type.
        return render_template('index.html')
    else:
        # Getting the user query.
        data = request.form['projectFilepath']

        # Converting the query into a user vector (tf-idf) form.
        vector = vectorizer.transform([data])[0].toarray()

        # Getting the indexes if the top 5 the most similar indexes.
        top_n = find_top_n(vector, X_sparse)

        # Sending the result to the template.
        return render_template('index2.html', names = names[top_n], search = data)