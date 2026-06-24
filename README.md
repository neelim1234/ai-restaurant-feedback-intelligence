# AI Restaurant Feedback Intelligence Platform

An AI-powered SaaS analytics platform that transforms raw restaurant customer reviews into actionable business insights using **FastAPI**, **PostgreSQL**, **React**, and **Gemini AI**.

---

## Problem Statement

Restaurants receive thousands of customer reviews across branches, cuisines, and service channels (delivery, dine-in, takeaway).

Manually analyzing these reviews is difficult because businesses need to answer questions like:

* Why are ratings dropping in Mumbai?
* Which branch is underperforming?
* Are delivery complaints increasing?
* What are the most common customer pain points?
* How should the business respond to negative reviews?

This project solves that by combining:

* Structured analytics
* Interactive dashboards
* AI-generated insights
* AI review response generation

---

## Key Features

### Analytics Engine

* Executive KPI dashboard
* Average rating tracking
* Complaint rate analysis
* Average wait time analysis
* Review volume monitoring

### Advanced Filtering

Supports multi-dimensional filtering by:

* City
* Brand
* Branch
* Cuisine
* Service channel
* Price segment
* Rating range
* Date range

This enables queries such as:

* Mumbai + Delivery + 1–2 stars
* Pune + Thai Bowl + Premium segment
* Bangalore + Dine-in + Last 30 days

---

### Branch Performance League

Compare branch performance across:

* Ratings
* Review count
* Wait times
* City-level performance

Helps identify top-performing and underperforming branches.

---

### Complaint Intelligence

Detects major complaint categories:

* Delivery Delay
* Food Quality
* Pricing
* Packaging
* Hygiene
* Staff Behavior
* Ambience
* Portion Size

---

### AI Executive Insights (Gemini)

The AI layer analyzes aggregated business metrics and generates:

* Executive summaries
* Root cause analysis
* Improvement recommendations

Example output:

* Mumbai delivery ratings are significantly below network average.
* Long delivery wait times are strongly correlated with low ratings.
* Increase delivery staffing during Friday/Saturday peak hours.

---

### AI Review Responder

Generate professional, empathetic responses to customer reviews.

Example:

**Customer Review:**
“Delivery took 55 minutes and food was cold.”

**AI Response:**
“Thank you for your feedback. We sincerely apologize for the delayed delivery and poor food quality. We are reviewing our delivery workflow to ensure this does not happen again.”

---

# Tech Stack

## Backend

* FastAPI
* PostgreSQL
* SQLAlchemy ORM
* Alembic Migrations
* Pydantic
* REST APIs

## Frontend

* React
* Zustand
* Tailwind CSS
* Recharts
* Axios
* React Router

## AI Layer

* Google Gemini API
* Prompt Engineering
* Structured JSON AI responses

---

# System Architecture

```text
Synthetic Dataset (8500 Reviews)
            ↓
      PostgreSQL Database
            ↓
     FastAPI Backend APIs
            ↓
     Analytics Engine Layer
            ↓
       React Dashboard
            ↓
        Gemini AI Layer
            ↓
  Insights + Review Responses
```

---

# Database Design

Normalized relational schema:

* organizations
* brands
* branches
* cities
* cuisines
* feedbacks
* feedback_analysis
* complaint_categories

Key design principles:

* Strong normalization
* Foreign key relationships
* Indexed analytics queries
* Clean filterable schema

---

# Dataset

Synthetic production-style dataset generated for realistic analytics.

Dataset includes:

* 8500 customer reviews
* 17 branches
* 4 brands
* 5 cities
* 5 cuisines
* 18-month timeline

Hidden business patterns were intentionally embedded, such as:

* Mumbai delivery underperformance
* Weekend review volume spikes
* Pune Thai Bowl pricing complaints
* Bangalore La Cucina high satisfaction

This makes analytics meaningful and realistic.

---

# Engineering Highlights

This project demonstrates:

* Backend architecture design
* Relational schema design
* Query optimization
* Analytics system design
* REST API development
* State management
* AI integration
* Product thinking

---

# Local Setup

## Clone Repository

```bash
git clone https://github.com/neelim1234/ai-restaurant-feedback-intelligence.git
cd ai-restaurant-feedback-intelligence
```

---

## Backend Setup

```bash
pip install -r requirements.txt
cd backend
```

Create `.env`

```env
DATABASE_URL=postgresql://username:password@localhost:5432/flagship_db
GEMINI_API_KEY=your_gemini_api_key_here
DEBUG=False
```

Run backend:

```bash
uvicorn main:app --reload --port 8000
```

Backend runs at:

```text
http://127.0.0.1:8000
```

Swagger docs:

```text
http://127.0.0.1:8000/docs
```

---

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at:

```text
http://localhost:5173
```

---

# Future Improvements

Potential production upgrades:

* Authentication & RBAC
* Multi-tenant SaaS support
* CSV upload pipeline
* Redis caching
* Background AI jobs
* Cloud deployment
* Real-time alerts
* PDF executive reports

---



