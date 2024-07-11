from flask import Flask, request, jsonify, render_template
import logging
from logging.handlers import RotatingFileHandler
import pickle
import pandas as pd
from sklearn.preprocessing import StandardScaler

app = Flask(__name__)
app.debug = True  # Enable Flask debug mode for detailed error messages

# Set up logging
handler = RotatingFileHandler('logs/app.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)

# Load the trained model and scaler
model_filename = 'models/trained_House_Price_Model1.pkl'
scaler_filename = 'models/scaler.pkl'

try:
    with open(model_filename, 'rb') as file:
        model = pickle.load(file)
    app.logger.info("Model loaded successfully.")
except Exception as e:
    app.logger.error(f"Error loading model: {e}")

try:
    with open(scaler_filename, 'rb') as file:
        scaler = pickle.load(file)
    app.logger.info("Scaler loaded successfully.")
except Exception as e:
    app.logger.error(f"Error loading scaler: {e}")

# Load the CSV file and get unique values
df = pd.read_csv('csv/Hyderbad_House_price.csv')
unique_titles = df['title'].unique()
unique_locations = df['location'].unique()
unique_building_statuses = df['building_status'].unique()

# Create mapping dictionaries for categorical features
title_mapping = {title: idx for idx, title in enumerate(unique_titles)}
location_mapping = {location: idx for idx, location in enumerate(unique_locations)}
building_status_mapping = {status: idx for idx, status in enumerate(unique_building_statuses)}

# Define the home route
@app.route('/')
def home():
    return render_template('index.html', titles=unique_titles, locations=unique_locations, building_statuses=unique_building_statuses)

# Define the predict route
@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json(force=True)
        app.logger.info(f"Received form data: {data}")

        # Ensure all fields are present
        required_fields = ['title', 'location', 'rate_persqft', 'area_insqft', 'building_status']
        for field in required_fields:
            if field not in data or data[field] is None:
                raise ValueError(f"Missing or None value for required field: {field}")

        # Convert categorical features to indices
        title_idx = title_mapping[data['title']]
        location_idx = location_mapping[data['location']]
        building_status_idx = building_status_mapping[data['building_status']]

        # Convert data types as needed
        input_data = [
            title_idx,
            location_idx,
            float(data['rate_persqft']),
            float(data['area_insqft']),
            building_status_idx
        ]
        app.logger.info(f"Input data: {input_data}")

        # Scale the input data
        input_data_scaled = scaler.transform([input_data])
        app.logger.info(f"Scaled input data: {input_data_scaled}")

        # Predict using the loaded model
        prediction = model.predict(input_data_scaled)
        app.logger.info(f"Prediction result: {prediction}")

        return jsonify({'predicted_price': float(prediction[0])})  # Ensure the prediction is converted to float
    except KeyError as e:
        app.logger.error(f"KeyError during prediction: {e}")
        return jsonify({'error': 'Invalid input data. Missing key in request.'}), 400
    except ValueError as e:
        app.logger.error(f"ValueError during prediction: {e}")
        return jsonify({'error': f'Invalid input data format. {str(e)}'}), 400
    except Exception as e:
        app.logger.error(f"Error during prediction: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500  # Return 500 status code for internal server error

if __name__ == '__main__':
    app.run(debug=True)
