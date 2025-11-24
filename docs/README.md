# Asset Management System Documentation

## Overview

The Asset Management System is a comprehensive web application for managing IT assets, built with a React frontend and FastAPI backend. It integrates with Snipe-IT for data synchronization and provides detailed asset tracking, user management, and reporting capabilities.

## Architecture

```
Frontend (React + TypeScript + Vite)
├── Dashboard with asset overview
├── Users management
├── Fun Queries for data analysis
├── PDF export functionality
└── Real-time data visualization

Backend (FastAPI + SQLModel + PostgreSQL)
├── Asset management API
├── User management API
├── Snipe-IT synchronization
├── PDF export service
└── Scheduled sync jobs

Database (PostgreSQL)
├── Assets table
├── Users table
└── Export history table
```

## Technology Stack

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **UI Components**: Custom components with Tailwind CSS
- **Charts**: Recharts for data visualization
- **HTTP Client**: Built-in fetch API

### Backend
- **Framework**: FastAPI with Python 3.13
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Database**: PostgreSQL
- **PDF Generation**: ReportLab
- **Scheduling**: APScheduler
- **HTTP Client**: Requests + aiohttp

### Infrastructure
- **Web Server**: IIS (Windows Server 2022)
- **Process Manager**: NSSM for backend service
- **CI/CD**: GitHub Actions
- **SSL**: Custom certificates
ment: http://localhost:8000/api
  

### Authentication
Currently, the API does not require authentication due to need to be on company network.

### Endpoints

#### Assets
- `GET /api/assets` - Get all assets
- `GET /api/assets/paginated` - Get assets with pagination
- `POST /api/assets/export-pdf` - Generate PDF export
- `GET /api/assets/export-history` - Get export history

#### Users
- `GET /api/users` - Get all users
- `GET /api/users/paginated` - Get users with pagination
- `GET /api/users/{user_id}` - Get specific user
- `GET /api/users/{user_id}/assets` - Get user's assets

#### Sync
- `POST /api/sync/assets` - Sync assets from Snipe-IT
- `POST /api/sync/users` - Sync users from Snipe-IT
- `POST /api/sync/all` - Full sync (assets + users)
- `GET /api/sync/schedule` - Get sync schedule
- `POST /api/sync/scheduler/start` - Start scheduler
- `POST /api/sync/scheduler/stop` - Stop scheduler

#### Fun Queries
- `GET /api/fun-queries/templates` - Get query templates
- `GET /api/fun-queries/execute/{template_id}` - Execute query

### Data Models

#### Asset
```typescript
{
  id: number;
  asset_name: string;
  asset_tag: string;
  serial: string;
  model: string;
  model_no: string;
  category: string;
  manufacturer: string;
  warranty: string;
  warranty_expires: string;
  location: string;
  department: string;
  assigned_user_name: string;
  status: string;
  company: string;
  created_at: string;
}
```

#### User
```typescript
{
  id: number;
  first_name: string;
  last_name: string;
  username: string;
  email: string;
  county: string;
  department_id: string;
  department_name: string;
  location_id: string;
  assets_count: number;
  license_count: number;
}
```

## Frontend Components

### Core Components
- **Dashboard**: Main overview with charts and statistics
- **AssetTable**: Display and filter assets
- **UserAssetsModal**: Show assets assigned to users
- **ExportModal**: Configure and generate PDF exports
- **QuerySelector**: Execute predefined data queries

### Charts
- **AssetChart**: General asset statistics
- **MacLenovoChart**: Mac vs Lenovo distribution by department
- **StatusPieChart**: Asset status distribution
- **TrendChart**: Asset trends over time
- **AssetLifecycleChart**: Asset lifecycle analysis
- **LaptopExpirationChart**: Warranty expiration tracking

### UI Components
- **Layout**: Main application layout
- **Card**: Reusable card component
- **Button**: Styled button variants
- **Input**: Form input components
- **Select**: Dropdown selection
- **Dialog**: Modal dialogs
- **Table**: Data table component
- **Badge**: Status and category badges

## Backend Services

### Core Services
- **Database Service**: SQLModel session management
- **Sync Service**: Snipe-IT data synchronization
- **PDF Export Service**: Report generation
- **Fun Queries Service**: Predefined data analysis queries
- **Performance Monitor**: System monitoring and circuit breaker

### Scheduled Jobs
- **Asset Sync**: Daily at 8am, 12pm, 4pm, 8pm
- **User Sync**: Daily at 8am, 12pm, 4pm, 8pm
- **Performance Monitoring**: Continuous monitoring

### Database Migrations
- Asset table creation
- User table creation
- Department name enhancement
- Export history table
- Warranty expiration date conversion

## Deployment

### Production Environment
- **Server**: Windows Server 2022 VM
- **Web Server**: IIS for frontend hosting
- **Backend Service**: NSSM-managed FastAPI service
- **Database**: PostgreSQL on same server
- **SSL**: Custom certificates

### CI/CD Pipeline
- **Repository**: GitHub
- **Secrets**: Single MYSECRETS environment variable
- **Deployment**: GitHub Actions workflow
- **Environment**: Production deployment to Windows Server

### Configuration
- **Environment Variables**: Stored in GitHub secrets
- **Database Connection**: PostgreSQL with connection pooling
- **Snipe-IT Integration**: API token and URL configuration
- **CORS**: Configured for production domains

## Development Setup

### Prerequisites
- Python 3.13+
- Node.js 18+
- PostgreSQL 12+
- Git

### Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend Setup
```bash
cd frontend
npm install
```

### Database Setup
```bash
cd backend
# Apply migrations
python -m alembic upgrade head
```

### Running Locally
```bash
# Backend (Terminal 1)
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Frontend (Terminal 2)
cd frontend
npm run dev
```

## Key Features

### Asset Management
- Complete asset lifecycle tracking
- Department and user assignment
- Warranty expiration monitoring
- Status tracking and updates
- Search and filtering capabilities

### User Management
- User profile management
- Department assignment
- Asset assignment tracking
- License count tracking

### Data Analysis
- Predefined query templates
- Custom data analysis
- Export capabilities
- Real-time charts and statistics

### Synchronization
- Automated Snipe-IT sync
- Background processing
- Error handling and retry logic
- Performance monitoring

### Reporting
- PDF export generation
- Configurable report content
- Export history tracking
- Multiple format support

### Logs
- Backend logs: Check application logs in Windows Event Viewer
- Frontend logs: Browser developer console
- Database logs: PostgreSQL log files

### Performance
- Monitor memory usage during large sync operations
- Check database query performance
- Verify network connectivity to Snipe-IT

## Security Considerations

### Current State
- No authentication implemented
- CORS configured for specific domains
- SSL certificates for HTTPS

## Maintenance

### Regular Tasks
- Monitor sync job success rates
- Review and clean up export history
- Update dependencies
- Backup database regularly

### Updates
- Frontend: Update npm packages
- Backend: Update Python packages
- Database: Apply new migrations
- Server: Windows updates and security patches

## Support

For technical support and issues:
1. Check the session documentation in `docs/session/`
2. Review application logs
3. Verify configuration settings
4. Test with sample data

