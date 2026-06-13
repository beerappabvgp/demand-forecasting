# 📈 Enterprise Demand Forecasting Platform

A production-grade **MLOps platform** that forecasts retail inventory demand using an ensemble of deep learning (PyTorch Transformer) and tree-based models (LightGBM), trained on the **Walmart M5 Forecasting dataset**. The system serves real-time next-day demand predictions through a REST API backed by a pre-computed feature store.

> **Status:** Production-Ready 🚀
>
> **Live Frontend:** [https://demand-forecasting-2vm3cv7dvxlhlapppvuxiqd.streamlit.app](https://demand-forecasting-2vm3cv7dvxlhlapppvuxiqd.streamlit.app)
>
> **API Health:** `http://demand-forecasting-alb-494652046.ap-south-1.elb.amazonaws.com/health`

---

## 🏆 Model Performance & Selection

Three models were trained, tracked with MLflow, and evaluated on a held-out validation set. The **Transformer was selected as the production champion**.

| Model | Val MAE | Val RMSE | vs LightGBM Baseline (MAE) |
|---|---|---|---|
| **Transformer (Prod)** | **0.9468** | 2.2409 | **-3.83% ✅** |
| LSTM | 0.9496 | **1.9118** | -3.55% ✅ |
| LightGBM | 0.9845 | 1.9800 | Baseline |

> **💡 Why Transformer despite a higher RMSE?** 
> In retail inventory forecasting, Mean Absolute Error (MAE) translates directly to "average units off per day." An MAE of ~0.95 means predictions are typically within 1 unit of actual sales. While RMSE heavily penalizes occasional large spikes (which are common in retail due to unpredictable bulk buys), minimizing MAE provides a more consistently accurate baseline for daily replenishment. We prioritize consistent daily accuracy over fitting rare anomalies.

---

## 🎯 Engineering Highlights 

This project moves beyond a Jupyter Notebook into a fully productionized system designed with enterprise constraints in mind:

- **FinOps & Cost Optimization:** Engineered a custom AWS Lambda + EventBridge scheduler to automatically spin down the ECS cluster and destroy the NAT Gateway outside of Indian Standard Time (IST) business hours (Mon-Fri 9AM-6PM), cutting AWS costs by over **70%** (saving ~$75-85/month).
- **Sub-100ms Inference Latency:** The FastAPI backend pre-loads 14-day historical rolling windows for all 30,000+ items into an in-memory feature store at startup, eliminating database lookup bottlenecks during API calls.
- **100% Infrastructure as Code:** The entire AWS environment (VPC, private subnets, ALB, ECR, ECS Fargate, IAM, S3, Glue, Lambda) is fully reproducible via 8 custom Terraform modules.
- **Zero-Downtime CI/CD:** GitHub Actions automatically builds the Docker serving container, pushes to Amazon ECR, and orchestrates a rolling update on ECS upon code merges to `main`.
- **Serverless Data Lake:** Utilizes AWS Glue (PySpark) for scalable, serverless data transformation (Bronze to Silver layer), converting raw CSVs into optimized Parquet formats.

---

## 📊 Dataset — Walmart M5 Forecasting

| Property | Value |
|---|---|
| **Source** | [Kaggle M5 Forecasting Accuracy Competition](https://www.kaggle.com/c/m5-forecasting-accuracy) |
| **Raw Sales File** | 115 MB (`sales_train_validation.csv`) |
| **Raw Prices File** | 194 MB (`sell_prices.csv`) |
| **Total Raw Data** | ~349 MB |
| **Sales records** | 30,490 unique item-store combinations × 1,913 days |
| **Time span** | 5+ years of daily sales history (2011–2016) |
| **Stores** | 10 Walmart stores across 3 US states (CA, TX, WI) |
| **Product categories** | Hobbies, Foods, Household |
| **Features engineered** | 16 features: lag-1, lag-7, lag-28; rolling means/stds (7/14/28 day); calendar features; SNAP flags; sell price |
| **Sequence window** | 14 days of history per prediction |

---

## 🌟 Business Impact

Inventory mismanagement costs retail businesses millions annually. This platform directly addresses three cost drivers:

- **Reduces stockouts** — Forecasting demand spikes 1 day ahead allows replenishment orders to be placed proactively
- **Minimises holding costs** — Accurate forecasts prevent over-ordering of slow-moving SKUs
- **Automates decisions** — Real-time REST API serves predictions at sub-100ms latency, removing manual analyst work
- **Cost-optimised infrastructure** — Automated scheduler shuts down all AWS resources outside business hours (Mon–Fri 9AM–6PM IST), saving ~$75–85/month vs 24/7 operation

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          DATA PIPELINE                                       │
│                                                                              │
│  Kaggle M5 Dataset ──► S3 Bronze (Raw) ──► AWS Glue (ETL) ──► S3 Silver    │
│                                               (PySpark)       (Parquet)     │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                          TRAINING PIPELINE                                   │
│                                                                              │
│  Feature Engineering (16 features) ──► MLflow Experiment Tracking           │
│                                                                              │
│  ┌──────────────┐    ┌────────────────────┐    ┌─────────────────────────┐  │
│  │  LightGBM    │    │    LSTM (PyTorch)   │    │ Transformer (PyTorch)   │  │
│  │ MAE: 0.9845  │    │   MAE: 0.9496      │    │ MAE: 0.9468 🏆 WINNER  │  │
│  └──────────────┘    └────────────────────┘    └─────────────────────────┘  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │  Export best model + scaler
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                          SERVING PIPELINE                                    │
│                                                                              │
│  models/transformer_model.pt ──► Feature Store (14-day windows, in-memory) │
│  models/transformer_scaler.pkl                                               │
│                │                                                             │
│                ▼                                                             │
│  FastAPI + Uvicorn (Docker) ──► Amazon ECR ──► AWS ECS Fargate              │
│                                                     │                        │
│                                              ALB (port 443/80)              │
│                                                     │                        │
│                                         ┌───────────▼──────────┐           │
│                                         │  Streamlit Frontend   │           │
│                                         │ (Streamlit Cloud)     │           │
│                                         └──────────────────────┘           │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

| Category | Technologies |
|---|---|
| **Machine Learning** | PyTorch (Transformer + LSTM), LightGBM, Scikit-Learn |
| **Experiment Tracking** | MLflow (local + S3 artifact store) |
| **Data Engineering** | Polars, PyArrow, AWS Glue (PySpark), S3 Data Lake (Bronze/Silver) |
| **API / Backend** | FastAPI, Uvicorn (2 workers), Pydantic |
| **Frontend** | Streamlit, Plotly |
| **Containerisation** | Docker (python:3.12-slim), Amazon ECR |
| **Compute** | AWS ECS Fargate (1 vCPU / 4 GB RAM) |
| **Networking** | AWS VPC, ALB, NAT Gateway, Private Subnets |
| **Storage** | AWS S3 (Bronze, Silver, MLflow buckets) |
| **IaC** | Terraform (8 modules: VPC, ALB, ECS, ECR, IAM, S3, Glue, Scheduler) |
| **CI/CD** | GitHub Actions (auto build + push to ECR on every `main` push) |
| **FinOps** | AWS Lambda + EventBridge scheduled auto-shutdown (Mon–Fri 9AM–6PM IST only) |

---

## 🚀 Key Features

### 1. Transformer-Based Time-Series Forecasting
- Custom `DemandTransformer` with sinusoidal Positional Encoding
- Architecture: `input_size=16 → d_model=64 → 4 heads → 2 encoder layers → FC → ReLU`
- Trained with Huber Loss to be robust to outlier sales spikes

### 2. Pre-computed Feature Store
- At startup, the API loads a 14-day rolling window for every item-store combination into memory
- Predictions are served in **< 100ms** with zero database queries at inference time
- Supports all 30,490 unique item-store combinations from the M5 dataset

### 3. Full MLflow Experiment Tracking
- Every training run (LightGBM, LSTM, Transformer) logs metrics, parameters, and artifacts
- `scripts/evaluate/compare_models.py` generates a side-by-side champion selection report
- Best model is automatically exported to `models/` for container packaging

### 4. Production-Ready API
- **`GET /health`** — ALB health check endpoint
- **`GET /valid-products`** — Lists all 30,490 forecastable item-store pairs
- **`POST /predict`** — Returns next-day demand forecast given `item_id` + `store_id`

### 5. Automated FinOps Scheduler
- **Lambda + EventBridge** automatically deletes the NAT Gateway and scales ECS to 0 at **6 PM IST** every weekday
- Recreates NAT Gateway and restores ECS to 1 task at **9 AM IST** every weekday
- Weekends (Saturday + Sunday) stay fully off
- Saves **~$75–85/month** vs running 24/7

### 6. Infrastructure as Code (100% Terraform)
All AWS infrastructure — VPC, subnets, NAT Gateway, ALB, ECR, ECS, IAM roles, S3 buckets, Glue jobs, Lambda scheduler — is defined in Terraform across 8 modules. A single `terraform apply` provisions the entire production environment.

---

## 💻 Running Locally

### Prerequisites
- Python 3.12+
- `models/transformer_model.pt` and `models/transformer_scaler.pkl` present
- `data/training/lightgbm_validation_dataset.parquet` present

### 1. Setup Environment
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-serving.txt   # Backend
pip install -r requirements.txt           # Full environment (training + dev)
```

### 2. Start the Backend API
```bash
uvicorn services.api.main:app --host 0.0.0.0 --port 8080 --reload
```
API will be available at `http://localhost:8080`

### 3. Start the Frontend
```bash
streamlit run frontend/app.py
```
Dashboard opens at `http://localhost:8501`

### 4. Make a Prediction
```bash
curl -X POST http://localhost:8080/predict \
  -H "Content-Type: application/json" \
  -d '{"item_id": "HOBBIES_1_001", "store_id": "CA_1"}'
```

---

## 📂 Project Structure

```
demand-forecasting-platform/
├── .github/
│   └── workflows/
│       └── deploy.yml           # CI/CD: auto build + push to ECR on main push
├── data/
│   ├── raw/m5/                  # Raw Kaggle M5 CSV files (~349 MB)
│   └── training/                # Feature-engineered Parquet datasets
├── frontend/
│   ├── app.py                   # Streamlit dashboard
│   └── requirements.txt         # Frontend-only dependencies
├── glue/                        # AWS Glue PySpark ETL scripts
├── models/
│   ├── transformer_model.pt     # Production model (1.7 MB, PyTorch)
│   ├── transformer_scaler.pkl   # Feature scaler
│   ├── lstm_model.pt            # LSTM baseline (217 KB)
│   └── lightgbm_model.pkl       # LightGBM baseline (1.1 MB)
├── notebooks/                   # Exploratory analysis notebooks
├── reports/                     # Forecast output CSVs
├── scripts/
│   ├── aws_sagemaker/           # SageMaker training job scripts
│   ├── dl/                      # DL training: train_lstm.py, train_transformer.py, export
│   ├── evaluate/
│   │   └── compare_models.py    # MLflow champion selection report
│   └── ops/
│       ├── start_all.sh         # Manually start all AWS resources via Lambda
│       └── stop_all.sh          # Manually stop all AWS resources via Lambda
├── services/
│   └── api/
│       ├── main.py              # FastAPI application (routes)
│       ├── model_service.py     # Feature store + inference logic
│       └── schemas.py           # Pydantic request/response models
├── src/
│   ├── models/
│   │   ├── dl/
│   │   │   ├── transformer.py   # DemandTransformer architecture
│   │   │   ├── lstm.py          # LSTM architecture
│   │   │   └── trainer.py       # PyTorch training loop
│   │   └── lightgbm/
│   │       └── trainer.py       # LightGBM training with MLflow
│   ├── features/                # Feature engineering pipeline
│   ├── training/
│   │   └── dataset_loader.py    # Parquet data loader
│   └── evaluation/              # Model evaluation utilities
├── terraform/
│   ├── main.tf                  # Root module — wires all 8 modules together
│   ├── modules/
│   │   ├── alb/                 # Application Load Balancer
│   │   ├── ecr/                 # Elastic Container Registry
│   │   ├── ecs/                 # ECS Fargate cluster + service
│   │   ├── glue/                # Glue ETL job
│   │   ├── iam/                 # All IAM roles and policies
│   │   ├── s3/                  # Bronze, Silver, MLflow S3 buckets
│   │   ├── scheduler/           # Lambda + EventBridge FinOps scheduler
│   │   └── vpc/                 # VPC, subnets, NAT Gateway, security groups
├── Dockerfile                   # Production container (python:3.12-slim)
├── requirements-serving.txt     # Minimal serving deps (FastAPI, PyTorch, LightGBM)
└── requirements.txt             # Full development dependencies
```

---

## ☁️ AWS Infrastructure

All resources are in **ap-south-1 (Mumbai)**.

| Service | Purpose |
|---|---|
| **S3** (3 buckets) | Bronze (raw), Silver (processed Parquet), MLflow artifacts |
| **AWS Glue** | PySpark ETL job: Bronze → Silver transformation |
| **Amazon ECR** | Docker image registry for the serving container |
| **AWS ECS Fargate** | Runs the FastAPI container (1 vCPU / 4 GB RAM) |
| **Application Load Balancer** | Public HTTPS entry point, routes to ECS |
| **VPC + NAT Gateway** | Private networking for ECS tasks |
| **Lambda + EventBridge** | FinOps scheduler (start/stop on IST business hours) |
| **IAM** | Least-privilege roles for ECS, Glue, SageMaker, Lambda |

---

## 🔧 Operations

### Manual Start/Stop (On-Demand)
```bash
# Start all resources right now (creates NAT GW + starts ECS)
bash scripts/ops/start_all.sh

# Stop all resources right now (stops ECS + deletes NAT GW)
bash scripts/ops/stop_all.sh
```

### Automatic Schedule
| Day | 9:00 AM IST | 6:00 PM IST |
|---|---|---|
| Mon–Fri | ✅ AUTO START | ✅ AUTO STOP |
| Saturday | ❌ Off all day | — |
| Sunday | ❌ Off all day | — |

### CI/CD Pipeline
Every push to `main` that touches `services/`, `src/`, `Dockerfile`, or `requirements-serving.txt` automatically:
1. Builds a new Docker image
2. Pushes it to Amazon ECR with the `:latest` tag
3. Forces a new ECS deployment to pick up the updated image

---