
# Import required libraries
import os
import streamlit as st
import pandas as pd
import requests

# Set the base URL of the Flask backend
BACKEND_URL = os.environ.get(
    "BACKEND_URL",
    "http://backend:7860"
).rstrip("/")

# Display the page title and description
st.markdown(
    """
    <div class="hero">
        <h1>🛒 SuperKart Sales Predictor</h1>
        <p>Enter product and store details to forecast total sales, or upload a CSV for batch predictions.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Collect product weight from the user
Product_Weight = st.number_input("Product Weight", min_value=0.0, value=12.66)

# Collect product sugar content from the user
Product_Sugar_Content = st.selectbox(
    "Product Sugar Content",
    ["Low Sugar", "Regular", "No Sugar"]
)

# Collect allocated area from the user
Product_Allocated_Area = st.number_input(
    "Product Allocated Area",
    min_value=0.0,
    value=0.027
)

# Collect product MRP from the user
Product_MRP = st.number_input(
    "Product MRP",
    min_value=0.0,
    value=117.08
)

# Collect store size from the user
Store_Size = st.selectbox(
    "Store Size",
    ["Small", "Medium", "High"]
)

# Collect city tier from the user
Store_Location_City_Type = st.selectbox(
    "Store Location City Type",
    ["Tier 1", "Tier 2", "Tier 3"]
)

# Collect store type from the user
Store_Type = st.selectbox(
    "Store Type",
    ["Supermarket Type1", "Supermarket Type2", "Departmental Store", "Food Mart"]
)

# Collect product ID category from the user
Product_Id_char = st.selectbox(
    "Product ID Character",
    ["FD", "DR", "NC"]
)

# Collect store age from the user
Store_Age_Years = st.number_input(
    "Store Age (Years)",
    min_value=0,
    max_value=50,
    value=16
)

# Collect product type category from the user
Product_Type_Category = st.selectbox(
    "Product Type Category",
    ["Perishables", "Non Perishables"]
)

# Create the JSON payload for prediction
product_data = {
    "Product_Weight": Product_Weight,
    "Product_Sugar_Content": Product_Sugar_Content,
    "Product_Allocated_Area": Product_Allocated_Area,
    "Product_MRP": Product_MRP,
    "Store_Size": Store_Size,
    "Store_Location_City_Type": Store_Location_City_Type,
    "Store_Type": Store_Type,
    "Store_Age_Years": Store_Age_Years,
    "Product_Id_char": Product_Id_char,
    "Product_Type_Category": Product_Type_Category
}

# Generate a prediction for a single record
if st.button("Predict", type="primary"):

    # Send the input data to the prediction API
    response = requests.post(
        f"{BACKEND_URL}/v1/predict",
        json=product_data
    )

    # Display the prediction result
    if response.status_code == 200:
        result = response.json()
        predicted_sales = result["Sales"]
        st.success(
            f"Predicted Product Store Sales Total: ₹{predicted_sales:.2f}"
        )
    else:
        st.error("Unable to connect to the prediction API.")

# Display batch prediction section
st.subheader("Batch Prediction")

# Upload a CSV file for batch predictions
uploaded_file = st.file_uploader(
    "Upload a CSV file",
    type=["csv"]
)

# Process the uploaded file
if uploaded_file is not None:

    # Preview the uploaded data
    preview_df = pd.read_csv(uploaded_file)

    # Display the first few rows
    st.write("Preview of uploaded data:")
    st.dataframe(
        preview_df.head(),
        use_container_width=True
    )

    # Reset file pointer before sending to API
    uploaded_file.seek(0)

    # Generate predictions for the uploaded file
    if st.button("Predict for Batch", type="primary"):

        # Send the file to the batch prediction API
        response = requests.post(
            f"{BACKEND_URL}/v1/predictbatch",
            files={"file": uploaded_file}
        )

        # Display prediction results if successful
        if response.status_code == 200:

            # Extract API response
            results = response.json()

            # Show success message
            st.success("Predictions completed successfully!")

            try:

                # Convert a list response to a DataFrame
                if isinstance(results, list):
                    df = pd.DataFrame(results)

                # Convert a dictionary response to a DataFrame
                elif isinstance(results, dict):

                    # Handle dictionaries containing scalar values
                    if all(
                        not isinstance(v, (list, dict))
                        for v in results.values()
                    ):
                        df = pd.DataFrame([results])

                    # Handle dictionaries containing arrays
                    else:
                        df = pd.DataFrame(results)

                # Handle any other response type
                else:
                    df = pd.DataFrame({"Result": [results]})

                # Display the prediction results
                st.dataframe(
                    df,
                    use_container_width=True
                )

            except Exception as e:

                # Display the raw response if conversion fails
                st.error(
                    f"Unable to display results as a table: {e}"
                )
                st.json(results)

        else:

            # Display API error details
            st.error(
                f"Prediction API returned HTTP {response.status_code}: "
                f"{response.text}"
            )
