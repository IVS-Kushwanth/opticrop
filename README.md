# OptiCrop

**OptiCrop** is an AI-powered crop recommendation platform built with Flask and scikit-learn. It analyzes soil nutrients (N, P, K), climate conditions, and rainfall to recommend the optimal crop using five machine learning algorithms.

## Features

- **Multi-algorithm prediction** — KNN, Logistic Regression, Decision Tree, Random Forest, K-Means
- **Interactive web UI** — Premium dark-green theme with Bootstrap 5, Chart.js, and AOS animations
- **AJAX predictions** — Real-time crop recommendations without page reload
- **Algorithm comparison** — Compare all models side-by-side
- **User dashboard** — Stats, prediction history, and analytics
- **REST API** — JSON endpoints at `/api/v1`
- **22 crop types** — Rice, maize, cotton, coffee, apple, and more

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Flask 3, SQLAlchemy, Flask-Migrate |
| ML | scikit-learn, pandas, numpy |
| Frontend | Bootstrap 5, Chart.js, AOS, Font Awesome |
| Database | SQLite (default) |

## Project Structure

```
OptiCrop/
├── app/
│   ├── ml/                  # ML algorithms & predictor
│   ├── models/              # SQLAlchemy models
│   ├── routes/              # Flask blueprints
│   ├── static/              # CSS, JS, assets
│   └── templates/           # Jinja2 templates
├── data/                    # Crop recommendation dataset
├── models/                  # Trained .pkl model files
├── scripts/                 # Training & seed scripts
├── ml_notebooks/            # Jupyter notebooks
├── tests/                   # pytest test suite
├── run.py                   # Application entry point
└── requirements.txt
```

## Prerequisites

- Python 3.10+
- pip

## Setup Instructions

### 1. Clone and enter the project

```bash
git clone <repository-url>
cd OptiCrop
```

### 2. Create a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
pip install pytest
```

### 4. Configure environment

Copy the example environment file and edit as needed:

```bash
cp .env.example .env
```

Key variables in `.env`:

```
SECRET_KEY=your-super-secret-key-change-this
DATABASE_URL=sqlite:///opticrop.db
FLASK_ENV=development
FLASK_DEBUG=1
FLASK_APP=run.py
```

### 5. Initialize the database

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

Or create tables directly:

```bash
python -c "from app import create_app; from app.extensions import db; app = create_app(); app.app_context().push(); db.create_all()"
```

### 6. Train ML models

Download the dataset and train all five models:

```bash
python scripts/train_models.py
```

This creates `models/scaler.pkl` and individual model files in `models/`.

### 7. (Optional) Seed sample data

```bash
python scripts/seed_db.py
```

### 8. Run the application

```bash
python run.py
```

Open [http://localhost:5000](http://localhost:5000) in your browser.

## Usage

### Web Interface

| URL | Description |
|-----|-------------|
| `/` | Landing page |
| `/predict` | Crop prediction form |
| `/compare` | Compare all algorithms |
| `/dashboard` | User dashboard |
| `/history` | Prediction history |
| `/analytics` | Chart.js analytics |
| `/login` | User login |
| `/register` | User registration |

### REST API

**GET `/api/v1/`** — API info

**POST `/api/v1/predict`** — Predict crop

```json
{
  "N": 90,
  "P": 42,
  "K": 43,
  "temperature": 25,
  "humidity": 80,
  "ph": 6.5,
  "rainfall": 200,
  "algorithm": "random_forest"
}
```

**GET `/api/v1/stats`** — Analytics data for charts

**GET `/api/v1/history`** — Prediction history

## Running Tests

```bash
pytest tests/ -v
```

## Jupyter Notebook

Explore EDA and model training in:

```
ml_notebooks/OptiCrop_Model_Training.ipynb
```

Launch Jupyter:

```bash
jupyter notebook ml_notebooks/
```

## Design System

| Token | Value |
|-------|-------|
| Primary | `#1a472a` |
| Accent | `#74c69d` |
| Gold | `#f4a261` |
| Dark BG | `#0d1b12` |

## Production Deployment

```bash
gunicorn -w 4 -b 0.0.0.0:8000 run:app
```

Set `FLASK_ENV=production` and use a production database URL in `.env`.

## License

MIT
