
import joblib
import pandas as pd
from flask import Flask, request, jsonify

# Create the Flask application
app = Flask('sales_predictor')

# Load the saved prediction model
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "superkart_model.joblib")

sales_model = joblib.load(MODEL_PATH)


@app.route("/", methods=["GET"])
def index():
    """Display a welcome message."""
    return "Welcome to the SuperKart Sales Prediction System!"


@app.route("/v1/predict", methods=["POST"])
def predict_single():
    """Predict sales for a single product."""

    product_data = request.get_json()

    # Prepare the input features
    feature_columns = [
        "Product_Weight",
        "Product_Sugar_Content",
        "Product_Allocated_Area",
        "Product_MRP",
        "Store_Size",
        "Store_Location_City_Type",
        "Store_Type",
        "Product_Id_char",
        "Store_Age_Years",
        "Product_Type_Category",
    ]

    input_record = {
        feature: product_data[feature]
        for feature in feature_columns
    }

    # Convert input into the format expected by the model
    product_df = pd.DataFrame([input_record])

    # Generate the sales prediction
    predicted_sales = float(sales_model.predict(product_df)[0])

    return jsonify({"Sales": predicted_sales})


@app.route("/v1/predictbatch", methods=["POST"])
def predict_multiple():
    """Predict sales for products uploaded as a CSV file."""

    uploaded_file = request.files["file"]

    # Load product data from the uploaded CSV
    products_df = pd.read_csv(uploaded_file)

    # Predict sales for all products
    sales_predictions = sales_model.predict(products_df)

    # Map each row index to its predicted sales value
    results = {
        str(index): round(float(value), 2)
        for index, value in enumerate(sales_predictions)
    }

    return jsonify(results)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860, debug=False)
