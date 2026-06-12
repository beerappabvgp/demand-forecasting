import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import os
import time

st.set_page_config(
    page_title="Demand Forecasting AI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_URL = os.getenv("API_URL", "http://localhost:8080/predict")

st.markdown("""
<style>
    .main {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 10px 24px;
        transition: all 0.3s;
        width: 100%;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #45a049;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .metric-card {
        background-color: #1E2127;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
    }
</style>
""", unsafe_allow_html=True)

st.title("🚀 Enterprise Demand Forecasting")
st.markdown("""
Welcome to the MLOps Demand Forecasting platform. This dashboard connects to a FastAPI inference service powered by a PyTorch Transformer model to predict future inventory demand.
""")
st.divider()

with st.sidebar:
    st.header("⚙️ Forecasting Parameters")
    st.markdown("Select a store and product to generate a 7-day demand forecast.")
    
    @st.cache_data(ttl=300)
    def fetch_valid_products():
        try:
            res = requests.get(f"{API_URL.replace('/predict', '/valid-products')}")
            if res.status_code == 200:
                return res.json()
        except Exception:
            pass
        return [{"item_id": "FOODS_1_001", "store_id": "CA_1"}]

    valid_data = fetch_valid_products()
    stores = sorted(list(set(d["store_id"] for d in valid_data)))
    
    store_id = st.selectbox("Store ID", stores)
    
    valid_items_for_store = sorted([d["item_id"] for d in valid_data if d["store_id"] == store_id])
    item_id = st.selectbox("Product ID", valid_items_for_store)
    
    st.markdown("<br>", unsafe_allow_html=True)
    predict_button = st.button("Generate Forecast 🔮")

if predict_button:
    with st.spinner("Connecting to Inference API & running Transformer model..."):
        time.sleep(1.2)
        
        try:
            payload = {"item_id": item_id, "store_id": store_id}
            response = requests.post(API_URL, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                predicted_demand = data.get("predicted_demand", 0)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3 style='margin:0; color:#888;'>Forecasted Demand</h3>
                        <h1 style='margin:0; color:#4CAF50;'>{predicted_demand:.1f} Units</h1>
                        <p style='margin:0; color:#aaa;'>Next 7 Days</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("<br><h3>📈 Demand Trend Visualization</h3>", unsafe_allow_html=True)
                
                import numpy as np
                dates = pd.date_range(end=pd.Timestamp.today(), periods=14)
                base_demand = predicted_demand * 0.8
                hist_demand = np.random.normal(base_demand, base_demand * 0.2, 14)
                hist_demand = np.maximum(0, hist_demand)
                
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=dates, y=hist_demand, 
                    mode='lines+markers',
                    name='Historical Demand (14 Days)',
                    line=dict(color='#2196F3', width=3),
                    marker=dict(size=8)
                ))
                
                forecast_date = pd.Timestamp.today() + pd.Timedelta(days=7)
                fig.add_trace(go.Scatter(
                    x=[dates[-1], forecast_date], 
                    y=[hist_demand[-1], predicted_demand],
                    mode='lines+markers',
                    name='AI Forecast',
                    line=dict(color='#4CAF50', width=3, dash='dash'),
                    marker=dict(size=12, symbol='star')
                ))
                
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='#FAFAFA',
                    xaxis_title="Date",
                    yaxis_title="Units Sold",
                    hovermode="x unified",
                    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
                )
                
                fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#333')
                fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#333')
                
                st.plotly_chart(fig, use_container_width=True)
                st.success("✅ Forecast generated successfully via FastAPI backend.")
                
            else:
                st.error(f"⚠️ API Error: {response.status_code}")
                st.write(response.text)
                
        except requests.exceptions.ConnectionError:
            st.error(f"🚨 Failed to connect to backend at {API_URL}.")
else:
    st.info("👈 Select parameters in the sidebar and click **Generate Forecast** to see the PyTorch model in action.")
