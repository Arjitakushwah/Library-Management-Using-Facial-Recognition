import cv2
import os
from sklearn.neighbors import KNeighborsClassifier
import pandas as pd
import joblib
from datetime import datetime
import numpy as np
from models import User
import uuid

def train_model():
    faces = []
    labels = []
    userlist = os.listdir('static/faces')
    for user in userlist:
        for imgname in os.listdir(f'static/faces/{user}'):
            img = cv2.imread(f'static/faces/{user}/{imgname}')
            resized_face = cv2.resize(img, (50, 50))
            faces.append(resized_face.ravel())
            labels.append(user)
    faces = np.array(faces)
    knn = KNeighborsClassifier(n_neighbors=5)
    knn.fit(faces,labels)
    joblib.dump(knn,'static/face_recognition_model.pkl')

def Student_data(filename):
    name = filename.split('_')[0]
    enrollment = filename.split('_')[1]

    student = User.query.filter_by(name=name, enrollment=enrollment).first()
    return (student)


# generate book-id
def generate_book_id():
    # Generate a UUID
    unique_id = uuid.uuid4()
    # Convert the UUID to hexadecimal representation and remove hyphens
    book_id = unique_id.hex
    return book_id


# generate category id 
def generate_category_id():
    category_id = uuid.uuid4().hex
    return category_id
