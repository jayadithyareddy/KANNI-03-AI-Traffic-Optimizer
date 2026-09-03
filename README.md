# KANNI-03 AI Traffic Optimizer

## Overview

KANNI-03 is an AI-based traffic prediction and optimization system designed to analyze vehicle traffic and predict congestion levels using machine learning.

The system accepts vehicle counts such as cars, bikes, buses, and trucks and provides a predicted traffic value, congestion level, and recommended traffic signal duration.

## Features

- Traffic prediction using machine learning
- Car, bike, bus, and truck vehicle counts
- Low, Medium, and High congestion classification
- Recommended traffic signal time
- Prediction history
- Total vehicles for each prediction
- Average traffic
- Highest traffic recorded
- Prediction count
- Prediction time
- Clear history functionality
- Interactive web dashboard
- Flask REST API

## Technologies Used

- Python
- Flask
- Flask-CORS
- XGBoost
- Scikit-learn
- Pandas
- NumPy
- HTML
- CSS
- JavaScript
- Git
- GitHub

## Project Structure

```text
KANNI-03/
├── backend/
│   ├── app.py
│   ├── utils.py
│   ├── requirements.txt
│   ├── traffic_model.pkl
│   ├── label_encoders.pkl
│   └── feature_columns.pkl
├── frontend/
│   └── index.html
├── dataset/
├── model/
├── .gitignore
└── README.md

