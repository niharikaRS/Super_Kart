
import streamlit as st
import pandas as pd
import requests

# Base URL of the Flask backend
BACKEND_URL = "http://backend:7860"

# ---------- Page setup ----------
st.set_page_config(
    page_title="SuperKart Sales Predictor",
    page_icon="🛒",
    layout="wide",
)

# ---------- Custom styling ----------
st.markdown(
    """
    <style>
    .block-container {padding-top: 2rem; max-width: 1100px;}

    .hero {
        background: linear-gradient(135deg, #0f766e 0%, #14b8a6 50%, #5eead4 100%);
        padding: 2rem 2.5rem;
        border-radius: 18px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 24px rgba(20, 184, 166, 0.25);
    }
    .hero h1 {margin: 0; font-size: 2.2rem; color: white;}
    .hero p {margin: 0.4rem 0 0 0; font-size: 1.05rem; opacity: 0.95;}

    .section-title {
        font-size: 1.1rem; font-weight: 600; color: #0f766e;
        border-left: 4px solid #14b8a6; padding-left: 10px;
        margin: 0.5rem 0 1rem 0;
    }

    .result-card {
        background: linear-gradient(135deg, #ecfdf5, #d1fae5);
        border: 1px solid #6ee7b7;
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        margin-top: 1rem;
    }
    .result-card .label {color: #065f46; font-size: 0.95rem; margin-bottom: 0.2rem;}
    .result-card .value {color: #047857; font-size: 2.6rem; font-weight: 700;}

    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #0f766e, #14b8a6);
        border: none; border-radius: 10px;
        padding: 0.6rem 1.5rem; font-weight: 600;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    div.stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(20, 184, 166, 0.4);
    }

    #MainMenu, footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Header ----------
st.markdown(
    """
    <div class="hero">
        <h1>🛒 SuperKart Sales Predictor</h1>
        <p>Enter product and store details to forecast total sales, or upload a CSV for batch predictions.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

tab_single, tab_batch = st.tabs(["🎯 Single Prediction", "📂 Batch Prediction"])

# ---------- Single prediction ----------
with tab_single:
    col_product, col_store = st.columns(2, gap="large")

    with col_product:
        st.markdown('<div class="section-title">📦 Product Details</div>', unsafe_allow_html=True)
        Product_Weight = st.number_input("Product Weight", min_value=0.0, value=12.66)
        Product_Sugar_Content = st.selectbox("Product Sugar Content", ["Low Sugar", "Regular", "No Sugar"])
        Product_Allocated_Area = st.number_input("Product Allocated Area", min_value=0.0, value=0.027, format="%.3f")
        Product_MRP = st.number_input("Product MRP (₹)", min_value=0.0, value=117.08)
        Product_Id_char = st.selectbox("Product ID Character", ["FD", "DR", "NC"])
        Product_Type_Category = st.selectbox("Product Type Category", ["Perishables", "Non Perishables"])

    with col_store:
        st.markdown('<div class="section-title">🏬 Store Details</div>', unsafe_allow_html=True)
        Store_Size = st.selectbox("Store Size", ["Small", "Medium", "High"])
        Store_Location_City_Type = st.selectbox("Store Location City Type", ["Tier 1", "Tier 2", "Tier 3"])
        Store_Type = st.selectbox(
            "Store Type",
            ["Supermarket Type1", "Supermarket Type2", "Departmental Store", "Food Mart"],
        )
        Store_Age_Years = st.slider("Store Age (Years)", min_value=0, max_value=50, value=16)

    # Create JSON payload
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
        "Product_Type_Category": Product_Type_Category,
    }

    st.write("")
    if st.button("🔮 Predict Sales", type="primary", use_container_width=True):
        with st.spinner("Calculating prediction..."):
            try:
                response = requests.post(f"{BACKEND_URL}/v1/predict", json=product_data, timeout=30)
                if response.status_code == 200:
                    predicted_sales = response.json()["Sales"]
                    st.markdown(
                        f"""
                        <div class="result-card">
                            <div class="label">Predicted Product Store Sales Total</div>
                            <div class="value">₹{predicted_sales:,.2f}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.error("The prediction API returned an error.")
            except requests.exceptions.RequestException:
                st.error("Unable to connect to the prediction API.")

# ---------- Batch prediction ----------
with tab_batch:
    st.markdown('<div class="section-title">📂 Upload a CSV file</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"], label_visibility="collapsed")

    if uploaded_file is not None:
        with st.expander("Preview uploaded data"):
            st.dataframe(pd.read_csv(uploaded_file).head(), use_container_width=True)
            uploaded_file.seek(0)  # reset pointer so the full file is sent below

        if st.button("🚀 Predict for Batch", type="primary", use_container_width=True):
            with st.spinner("Running batch predictions..."):
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/v1/predictbatch",
                        files={"file": uploaded_file},
                        timeout=120,
                    )

                    if response.status_code == 200:
                        results = response.json()
                        st.success("Predictions completed successfully!")

                        try:
                            if isinstance(results, list):
                                df = pd.DataFrame(results)
                            elif isinstance(results, dict):
                                if all(not isinstance(v, (list, dict)) for v in results.values()):
                                    df = pd.DataFrame([results])
                                else:
                                    df = pd.DataFrame(results)
                            else:
                                df = pd.DataFrame({"Result": [results]})

                            st.dataframe(df, use_container_width=True)
                            st.download_button(
                                "⬇️ Download results as CSV",
                                df.to_csv(index=False).encode("utf-8"),
                                file_name="superkart_predictions.csv",
                                mime="text/csv",
                            )

                        except Exception as e:
                            st.error(f"Unable to display results as a table: {e}")
                            st.json(results)
                    else:
                        st.error("The prediction API returned an error.")
                except requests.exceptions.RequestException:
                    st.error("Unable to connect to the prediction API.")
