from flask import Flask, render_template, request
import pandas as pd
import requests
from io import BytesIO

app = Flask(__name__)

df = pd.read_csv("Medicine_Details.csv")

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    image_data = None
    if request.method == 'POST':
        medicine_name = request.form['medicine'].strip().lower()
        filtered_data = df[df['Medicine Name'].str.lower().str.contains(medicine_name)]
        if not filtered_data.empty:
            selected = filtered_data.iloc[0]
            result = {
                'name': selected['Medicine Name'],
                'uses': selected['Uses'],
                'composition': selected['Composition'],
                'side_effects': selected['Side_effects'],
                'manufacturer': selected['Manufacturer'],
                'review': selected['Average Review %'],
            }
            try:
                response = requests.get(selected['Image URL'])
                image_data = response.content
            except:
                image_data = None
    return render_template('index.html', result=result, image_data=image_data)
