# 🚀 AWARE: AI-Based Workplace Assessment for Readiness and Safety

![AWARE Logo](https://img.shields.io/badge/AWARE-Fit_to_Work-blue?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![TensorFlow](https://img.shields.io/badge/TensorFlow-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)

A web-based fit-to-work screening system that detects employee fatigue in under 30 seconds using Computer Vision (EAR/MAR analysis via MediaPipe) combined with self-reported health data to prevent workplace accidents.

## 🌟 Key Features

*   **Hybrid Fatigue Detection**: Combines geometric facial analysis (MediaPipe) and Deep Learning-based detection (MobileNetV2 CNN) for maximum accuracy in assessing work readiness.
*   **Real-time Analysis**: Processes webcam feed in real-time to analyze Eye Aspect Ratio (EAR) and Mouth Aspect Ratio (MAR) to detect signs of drowsiness and yawning.
*   **Holistic Risk Scoring**: Intelligently combines visual metrics with user self-reported health data (sleep hours, energy levels).
*   **Comprehensive Dashboard**: Admin dashboard for monitoring employee readiness, history, and aggregate fatigue statistics.
*   **Fast & Efficient**: Designed to complete the fit-to-work screening process in under 30 seconds.

## 🧠 Model Architecture

The AWARE system utilizes a hybrid approach:
1.  **MediaPipe Integration**: Analyzes physical metrics such as EAR (*Eye Aspect Ratio*) and MAR (*Mouth Aspect Ratio*).
2.  **CNN MobileNetV2**: Analyzes facial texture and features holistically with *automatic face cropping*.

For an in-depth technical explanation of the model architecture, calculation formulas, and *risk scoring* logic, please read:
👉 **[Hybrid Fatigue Detection Documentation](MODEL_EXPLANATION.md)**

## 💻 Tech Stack

### Frontend
*   **React 18** (Vite)
*   **Tailwind CSS** for styling
*   **Recharts** for data visualization
*   **Axios** for API requests
*   **Lucide React** for icons

### Backend
*   **FastAPI** for high-performance REST API
*   **SQLAlchemy** (ORM) & **PyMySQL**
*   **JWT (Python-Jose)** for Authentication
*   **OpenCV & MediaPipe** for image/video processing
*   **TensorFlow** (CPU) for inference

### Machine Learning Model
*   **TensorFlow / Keras**
*   **MobileNetV2** (Base architecture)

## 📂 Project Structure

```text
capstone-aware-project/
├── backend/                # FastAPI backend source code
│   ├── core/               # Configuration and security
│   ├── models/             # SQLAlchemy database models
│   ├── routers/            # API endpoint handlers
│   ├── schemas/            # Pydantic validation schemas
│   └── services/           # Business logic and ML integration
├── frontend/               # React (Vite) frontend source code
│   ├── src/                # UI components, pages, and hooks
│   └── public/             # Static assets
├── model/                  # ML model training and inference scripts
│   ├── api/                # Model serving API (if standalone)
│   ├── notebooks/          # Jupyter notebooks for EDA and training
│   └── src/                # Model building and utility scripts
├── docs/                   # Additional documentation
├── Dockerfile              # Docker configuration
├── MODEL_EXPLANATION.md    # Detailed ML documentation
└── README.md               # Project documentation (You are here)
```

## 🛠️ Local Setup Instructions

### Prerequisites
*   Node.js (v18+)
*   Python (3.9+)
*   MySQL Server

### 1. Clone the repository
```bash
git clone https://github.com/sekarwidhastri/AWARE.git
cd capstone-aware-project
```

### 2. Backend Setup
```bash
cd backend
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate
# Activate virtual environment (Mac/Linux)
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your MySQL database credentials

# Run database migrations / init script
python init_db.py

# Start the FastAPI server
uvicorn main:app --reload --port 8000
```
*Backend API will be available at `http://localhost:8000` (Swagger UI at `/docs`)*

### 3. Frontend Setup
Open a new terminal window:
```bash
cd frontend

# Install dependencies
npm install

# Start the Vite development server
npm run dev
```
*Frontend app will be available at `http://localhost:5173`*

## 🐳 Docker Deployment

The project includes a `Dockerfile` for easy deployment.
```bash
# Build the Docker image
docker build -t aware-app .

# Run the container
docker run -p 7860:7860 aware-app
```

## 📜 License

This project is part of the Capstone Project (CC26-PRU440). All rights reserved.