from flask import Flask, request, render_template
import pandas as pd
import requests
from io import BytesIO
import base64

app = Flask(__name__)

# Load your CSV once when the app starts
df = pd.read_csv("Medicine_Details.csv")

@app.route('/', methods=['GET', 'POST'])
def index():
    medicine_info = None
    image_data = None
    error_msg = None
    
    if request.method == 'POST':
        medicine_name = request.form.get('medicine_name', '').strip().lower()
        filtered_data = df[df['Medicine Name'].str.lower().str.contains(medicine_name)]
        
        if filtered_data.empty:
            error_msg = "❌ No medicine found with that name."
        else:
            selected = filtered_data.iloc[0]
            medicine_info = {
                "Uses": selected["Uses"],
                "Medicine Name": selected["Medicine Name"],
                "Composition": selected["Composition"],
                "Side Effects": selected["Side_effects"],
                "Manufacturer": selected["Manufacturer"],
                "Average Review": selected["Average Review %"]
            }
            # Fetch image and convert to base64 string to embed in HTML
            try:
                response = requests.get(selected["Image URL"])
                img_bytes = BytesIO(response.content).getvalue()
                image_data = base64.b64encode(img_bytes).decode('utf-8')
            except Exception as e:
                error_msg = f"⚠ Failed to load image: {e}"
    
    return render_template('index.html', medicine_info=medicine_info, image_data=image_data, error_msg=error_msg)

if __name__ == '__main__':
    app.run(debug=True)