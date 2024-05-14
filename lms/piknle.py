import os
import cv2
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
import pandas as pd
import joblib

# Load the trained model
knn = joblib.load('static/face_recognition_model.pkl')

# Extract features and labels
faces = knn._fit_X
labels = knn._y

# Convert faces to DataFrame
df = pd.DataFrame(faces)

# Add labels to DataFrame
df['label'] = labels

# Save DataFrame to CSV
df.to_csv('static/face_recognition_model.csv', index=False)