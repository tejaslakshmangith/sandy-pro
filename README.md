# Sandy Pro — Rock, Mineral & Ore Classification for Smart Mining Operations

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-green)](https://flask.palletsprojects.com)
[![Gemini](https://img.shields.io/badge/Gemini-2.5_Pro-orange)](https://ai.google.dev)

Sandy Pro is a full-stack web application for classifying rocks, minerals, and ores using AI-powered analysis. It combines **Google Gemini 2.5 Pro** for deep geological analysis with a **scikit-learn** ML fallback, served via a **Flask** backend with a rich dark-themed HTML/CSS/JS frontend.

## Features

- Gemini 2.5 Pro deep geological analysis with structured JSON output
- Gemini 2.5 Flash fast text-based classification
- A1–C2 Quality Grading based on purity percentage
- scikit-learn RandomForest fallback when Gemini API is unavailable
- Drag-and-drop image upload (PNG, JPG, JPEG, WEBP, BMP up to 16MB)
- Full classification report — elements, uses, market value, mining suitability
- Analytics Dashboard with Chart.js visualizations
- Dataset Browser with search, filter, sort, and pagination (337+ records)
- Docker support for easy deployment

## Tech Stack

| Layer | Technology |
|---|---|
| AI Analysis | Google Gemini 2.5 Pro |
| Fast Scoring | Google Gemini 2.5 Flash |
| ML Fallback | scikit-learn RandomForestClassifier |
| Backend | Python 3.11 + Flask 3.0 |
| Data | pandas, numpy |
| Charts | Chart.js 4.x (CDN) |
| Frontend | Vanilla HTML5 / CSS3 / JavaScript |
| Deployment | Docker + Gunicorn |

## Quick Start

### Local Setup

```bash
git clone https://github.com/tejaslakshmangith/sandy-pro.git
cd sandy-pro
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env — add GEMINI_API_KEY
python ml_models/train_model.py   # optional: pre-train ML fallback
python app.py
```

Open http://localhost:5000

### Docker

```bash
cp .env.example .env
# Add GEMINI_API_KEY to .env
docker-compose up --build
```

## Environment Variables

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Google Gemini API key (get from https://aistudio.google.com/) |
| `SECRET_KEY` | Flask session secret |
| `FLASK_ENV` | Flask environment (development/production) |

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | /api/health | Health check |
| POST | /api/classify | Classify a sample (image or description) |
| GET | /api/dataset | Paginated, filtered dataset |
| GET | /api/dataset/export | Export dataset as CSV |
| GET | /api/dashboard/stats | Aggregated statistics |

## Grade Scale

| Grade | Purity | Description |
|---|---|---|
| A1 | >= 95% | Premium Export Quality |
| A2 | 85-94% | High Commercial Grade |
| A3 | 75-84% | Standard Industrial Grade |
| B1 | 65-74% | Low Industrial Grade |
| B2 | 55-64% | Processing Required |
| B3 | 45-54% | Heavy Processing Needed |
| C1 | 30-44% | Marginal Viability |
| C2 | < 30% | Waste/Gangue Material |

## Dataset

337+ records covering ores, minerals, rocks, and gemstones across all quality grades A1-C2.
Columns: id, name, category, chemical_formula, color, hardness_mohs, luster, streak, cleavage, fracture, specific_gravity, crystal_system, formation_type, primary_elements, purity_percentage, quality_grade, commercial_value, industrial_uses, mining_region, market_value_usd_per_ton, extraction_difficulty, environmental_impact

## ML Model Training

```bash
python ml_models/train_model.py
```

Trains a RandomForestClassifier and saves to ml_models/classifier.pkl.
