# Asset Management System Documentation

## Overview

The Asset Management System is a full-stack web application designed to track and manage IT assets across multiple companies. It provides a comprehensive dashboard with analytics, filtering capabilities, and detailed asset information.

## Architecture

This is a modern full-stack application with the following architecture:

- **Frontend**: React 19 + TypeScript + Vite
- **Backend**: FastAPI + SQLAlchemy + PostgreSQL
- **Database**: PostgreSQL 16
- **Containerization**: Docker + Docker Compose
- **Reverse Proxy**: Traefik v3.0
- **Charts**: Recharts
- **Styling**: Tailwind CSS 4.1 + Radix UI

## Quick Start

### Prerequisites

- **Windows Server 2022** - Production environment
- **IIS** - Web server for frontend hosting
- **NSSM** - Windows service management for backend
- **PostgreSQL 16** - Database server
- **Node.js 18+** - Frontend build and local development
- **Python 3.11+** - Backend development

### Production Deployment

The application is deployed on Windows Server 2022 using:
- **IIS** for frontend hosting
- **NSSM** for backend service management
- **GitHub Actions** for CI/CD automation
- **PostgreSQL** for database

### Local Development

For local development, you can use Docker or run services directly:

#### Option A: Docker (Development Only)
```bash
docker-compose up -d
```

#### Option B: Direct Installation
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

### Local Development

#### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
Asset-Management/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── main.py         # FastAPI application entry point
│   │   ├── models.py       # SQLModel database models
│   │   ├── db.py           # Database configuration
│   │   └── routers/        # API route handlers
│   ├── alembic/            # Database migrations
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── hooks/          # Custom React hooks
│   │   ├── types/          # TypeScript type definitions
│   │   └── lib/            # Utility functions
│   └── package.json        # Node.js dependencies
├── docs/                   # Documentation
└── docker-compose.yaml     # Container orchestration
```

## Features

### Asset Management
- Track IT assets across multiple companies
- Filter assets by company, manufacturer, category, and model
- View asset status (Active, Pending Rebuild, Stock)
- Monitor warranty expiration dates

### Analytics Dashboard
- Asset distribution by category
- Status distribution pie chart
- Monthly asset trends
- Warranty expiration trends
- Detailed asset table with filtering

### Data Integration
- Snipe-IT API integration for asset synchronization
- PostgreSQL database for data persistence
- RESTful API for frontend communication

## API Documentation

The backend provides a RESTful API with the following endpoints:

- `GET /api/assets` - Retrieve all assets
- `POST /api/sync` - Synchronize assets from Snipe-IT
- Additional endpoints for asset management

API documentation is available at `http://localhost:8000/docs` when running the backend.

## Database Schema

The main `Asset` model includes:
- Basic identification (asset_name, asset_tag, model_no)
- Company and location information
- Hardware details (manufacturer, model, serial)
- Warranty information
- Status tracking
- Timestamps

## Deployment

The application is deployed on Windows Server 2022 using:
- **IIS** for frontend hosting with static file serving
- **NSSM** for backend service management and auto-restart
- **PostgreSQL** database server
- **GitHub Actions** for automated CI/CD pipeline
- **Windows Services** for reliable backend operation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

See LICENSE file for details. 