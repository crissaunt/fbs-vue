# Flight Booking System (FBS) - Technical Documentation

This document provides a comprehensive guide for installing, understanding, and maintaining the Flight Booking System.

---

## 1. System Architecture Overview

The system is built using a **Decoupled Architecture**:
- **Frontend**: Single Page Application (SPA) built with Vue.js 3.
- **Backend**: RESTful API built with Django 6.0 and Django REST Framework.
- **Database**: PostgreSQL hosted on Supabase.
- **Communication**: The Frontend communicates with the Backend via HTTP requests using Axios.

---

## 2. Backend (fbs_backend)

The backend is responsible for data persistence, business logic, and security.

### Tech Stack
- **Framework**: Django 6.0
- **API**: Django REST Framework (DRF)
- **Authentication**: JWT (JSON Web Tokens) via Djoser
- **Database**: PostgreSQL (Supabase)

### Key Directories
- `fbs_backend/`: Project configuration (settings, URLs, WSGI).
- `fbs_instructor/`: Core application logic, models for flights, bookings, and student data.
- `flightapp/`: Additional logic related to flight management.
- `requirements.txt`: List of all Python dependencies.

### Installation (Local)
1. Navigate to the backend folder: `cd fbs_backend`
2. Create a virtual environment: `python -m venv env`
3. Activate it: `env\Scripts\activate` (Windows) or `source env/bin/activate` (Mac/Linux)
4. Install dependencies: `pip install -r requirements.txt`
5. Set up `.env` file (see section 4).
6. Run migrations: `python manage.py migrate`
7. Start server: `python manage.py runserver`

---

## 3. Frontend (bookingapp)

The frontend provides a responsive and dynamic user interface.

### Tech Stack
- **Framework**: Vue.js 3 (Composition API)
- **Build Tool**: Vite
- **Styling**: Tailwind CSS 4
- **State Management**: Pinia
- **Routing**: Vue Router

### Key Directories
- `src/views/`: Individual pages (Login, Dashboard, Booking, etc.).
- `src/components/`: Reusable UI elements (Navbar, FlightCards, Loaders).
- `src/services/api/`: Axios configuration and API call functions.
- `src/stores/`: Pinia stores for user authentication and booking state.

### Installation (Local)
1. Navigate to the frontend folder: `cd bookingapp`
2. Install dependencies: `npm install`
3. Set up `.env` file (see section 4).
4. Start development server: `npm run dev`
5. Build for production: `npm run build`

---

## 4. Environment Variables (.env)

Both parts of the system require a `.env` file to store sensitive keys.

### Backend `.env`
```env
DEBUG=True
SECRET_KEY=your_random_secret_key
DATABASE_URL=postgresql://postgres:[PASSWORD]@[HOST]:[PORT]/postgres
ALLOWED_HOSTS=localhost,127.0.0.1,fbs-vue.onrender.com
CORS_ALLOWED_ORIGINS=http://localhost:5173,https://fbs-lms.netlify.app
```

### Frontend `.env`
```env
VITE_API_URL=https://fbs-vue.onrender.com
```

---

## 5. Deployment Workflow

### Production Setup
1.  **Database**: Hosted on **Supabase**. Ensure the "Connection Pooler" (Port 6543) is used for Render connections.
2.  **Backend**: Hosted on **Render**. 
    - Build Command: `pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate`
    - Start Command: `gunicorn fbs_backend.wsgi`
3.  **Frontend**: Hosted on **Netlify**.
    - Build Command: `npm run build`
    - Publish Directory: `dist`
    - Environment Variable: `VITE_API_URL` pointing to the Render backend.

### Maintenance (The "Stay Awake" Cron)
To prevent the Render free tier from sleeping, a cron job (via cron-job.org) pings the backend URL every 14 minutes.

---

## 6. Security Features
- **CORS Protection**: Only the approved Netlify domain can access the API.
- **CSRF Protection**: Enabled for all form submissions.
- **Token-based Auth**: Secure login without storing passwords in the browser.
- **SSL/TLS**: All communication is encrypted via HTTPS.
