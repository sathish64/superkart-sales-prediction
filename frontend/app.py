
import streamlit as st
import pandas as pd
import requests

# Flask backend URL
BACKEND_URL = "http://172.18.0.1:7860"

# Configure the Streamlit page
st.set_page_config(
    page_title="SuperKart Sales Prediction",
    page_icon="🛒",
    layout="wide"
)

st.title("SuperKart Sales Prediction System")
st.write(
    "Enter the product and store details to estimate total product sales."
)

# Product and store input fields
product_weight = st.number_input(
    "Product Weight",
    min_value=0.0,
    value=12.66
)

sugar_content = st.selectbox(
    "Product Sugar Content",
    ["Low Sugar", "Regular", "No Sugar"]
)

allocated_area = st.number_input(
    "Product Allocated Area",
    min_value=0.0,
    value=0.027
)

product_mrp = st.number_input(
    "Product MRP",
    min_value=0.0,
    value=117.08
)

store_size = st.selectbox(
    "Store Size",
    ["Small", "Medium", "High"]
)

city_type = st.selectbox(
    "Store Location City Type",
    ["Tier 1", "Tier 2", "Tier 3"]
)

store_type = st.selectbox(
    "Store Type",
    [
        "Supermarket Type1",
        "Supermarket Type2",
        "Supermarket Type3",
        "Departmental Store",
        "Food Mart"
    ]
)

Product_Id_char = st.selectbox(
    "Product ID Character",
    ["FD", "DR", "NC"]
)

store_age = st.number_input(
    "Store Age (Years)",
    min_value=0,
    value=16
)

product_category = st.selectbox(
    "Product Type Category",
    ["Perishables", "Non Perishables"]
)

# Prepare the prediction request
product_data = {
    "Product_Weight": product_weight,
    "Product_Sugar_Content": sugar_content,
    "Product_Allocated_Area": allocated_area,
    "Product_MRP": product_mrp,
    "Store_Size": store_size,
    "Store_Location_City_Type": city_type,
    "Store_Type": store_type,
    "Product_Id_char": Product_Id_char,
    "Store_Age_Years": store_age,
    "Product_Type_Category": product_category
}

# Single product prediction
if st.button("Predict Sales", type="primary"):
    try:
        with st.spinner("Predicting sales..."):
            response = requests.post(
                f"{BACKEND_URL}/v1/predict",
                json=product_data,
                timeout=30
            )

        if response.ok:
            prediction = response.json()
            predicted_sales = prediction["Sales"]

            st.success(
                f"Predicted Product Store Sales Total: ₹{predicted_sales:.2f}"
            )
        else:
            st.error(
                f"Prediction failed. Backend returned status "
                f"{response.status_code}."
            )

    except requests.exceptions.RequestException as error:
        st.error(f"Could not connect to the prediction API: {error}")
    except (ValueError, KeyError, TypeError) as error:
        st.error(f"Unable to process the prediction response: {error}")


# Batch prediction section
st.divider()
st.subheader("Batch Prediction")
st.write("Upload a CSV file to generate predictions for multiple products.")

uploaded_file = st.file_uploader(
    "Choose a CSV file",
    type=["csv"]
)

if uploaded_file is not None:
    if st.button("Predict Batch Sales", type="primary"):
        try:
            with st.spinner("Processing batch predictions..."):
                response = requests.post(
                    f"{BACKEND_URL}/v1/predictbatch",
                    files={
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            "text/csv"
                        )
                    },
                    timeout=120
                )

            if response.ok:
                results = response.json()

                st.success("Batch predictions completed successfully!")

                # Convert the API response into a DataFrame
                if isinstance(results, list):
                    results_df = pd.DataFrame(results)

                elif isinstance(results, dict):
                    if all(
                        not isinstance(value, (list, dict))
                        for value in results.values()
                    ):
                        results_df = pd.DataFrame([results])
                    else:
                        results_df = pd.DataFrame(results)

                else:
                    results_df = pd.DataFrame(
                        {"Result": [results]}
                    )

                st.dataframe(
                    results_df,
                    use_container_width=True
                )

                # Allow users to download the predictions
                csv_data = results_df.to_csv(index=False).encode("utf-8")

                st.download_button(
                    label="Download Predictions as CSV",
                    data=csv_data,
                    file_name="superkart_predictions.csv",
                    mime="text/csv"
                )

            else:
                st.error(
                    f"Batch prediction failed. Backend returned status "
                    f"{response.status_code}."
                )

        except requests.exceptions.RequestException as error:
            st.error(f"Could not connect to the prediction API: {error}")
        except (ValueError, TypeError) as error:
            st.error(f"Unable to process batch results: {error}")
