# 📈 Enterprise Demand Forecasting Platform

An end-to-end MLOps platform that predicts retail inventory demand using deep learning (PyTorch Transformers) and tree-based models (LightGBM). This system reduces potential out-of-stock events by analyzing historical sales data and generating a 7-day demand forecast.

> **Status:** Production-Ready 🚀
> 
> **Live Demo:** [Placeholder: Add your Streamlit Cloud Link Here]

## 🌟 Business Impact
Inventory mismanagement costs retail businesses millions annually. This platform:
- **Reduces stockouts** by accurately forecasting high-demand periods.
- **Minimizes holding costs** by preventing over-ordering of slow-moving items.
- **Automates decision making** by serving real-time predictions via an API.

---

## 🏗️ Architecture

This project was built with two primary architectures: a full-scale Enterprise Cloud setup for production, and a Serverless/Lite setup for portfolio demonstration.

### 1. Enterprise Production Architecture (AWS)
Built entirely using Infrastructure as Code (Terraform), this pipeline scales to process terabytes of data.

`Data Lake (S3 Bronze) ➡️ AWS Glue (ETL to Silver) ➡️ Amazon SageMaker (Training) ➡️ ECR (Docker) ➡️ FastAPI (Inference)`

### 2. Serverless Demo Architecture (Zero Cost)
To host the platform continuously without incurring AWS costs, a "lite" version of the model is served using free-tier services.

`GitHub Repo ➡️ Render (FastAPI Docker) ➡️ Streamlit Community Cloud (Frontend UI)`

---

## 🛠️ Technology Stack

| Category | Technologies Used |
|----------|-------------------|
| **Machine Learning** | PyTorch (Transformers), LightGBM, Scikit-Learn |
| **Data Engineering** | Polars, PyArrow, AWS Glue (PySpark), S3 Data Lake |
| **Backend / API** | FastAPI, Uvicorn, Pydantic |
| **Frontend / UI** | Streamlit, Plotly |
| **DevOps & Cloud** | Docker, Terraform, AWS (ECR, SageMaker, VPC, IAM) |

---

## 🚀 Features
- **Transformer-based Forecasting:** Uses self-attention mechanisms to learn complex temporal patterns in retail data.
- **Feature Store Integration:** Automatically compiles and normalizes 14-day historical windows for instant API lookup.
- **Infrastructure as Code:** 100% of the AWS environment (Networking, IAM, Storage, Compute) is defined in Terraform.
- **Lite Mode:** A memory-optimized API configuration that runs on a 512MB RAM constraint for free-tier deployments.
- **Interactive UI:** A premium Streamlit dashboard for non-technical stakeholders to test predictions.

---

## 💻 How to Run Locally

### 1. Setup the Environment
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-serving.txt
pip install -r requirements-frontend.txt
```

### 2. Start the Backend API (FastAPI)
The backend serves the PyTorch model and the Feature Store.
```bash
# Run the API in Lite Mode (to save memory)
LITE_MODE=true uvicorn services.api.main:app --port 8080 --reload
```
*The API will be available at `http://localhost:8080`*

### 3. Start the Frontend Dashboard (Streamlit)
Open a new terminal, activate the virtual environment, and run:
```bash
streamlit run frontend/app.py
```
*The UI will automatically open in your browser at `http://localhost:8501`*

---

## 📂 Project Structure
```text
demand-forecasting-platform/
├── data/                  # Local data storage (Bronze/Silver/Gold)
├── frontend/              # Streamlit User Interface
│   └── app.py             # Dashboard code
├── glue/                  # AWS Glue ETL scripts
├── models/                # Saved PyTorch (.pt) and LightGBM models
├── scripts/               # Automation & Cloud deployment scripts
├── services/              # FastAPI Application
│   └── api/               # API endpoints and Model Serving logic
├── src/                   # Core ML source code (Training, Validation, Data Loaders)
├── terraform/             # AWS Infrastructure as Code (IaC)
├── Dockerfile             # Production container definition
├── requirements*.txt      # Dependency management
└── README.md
```

