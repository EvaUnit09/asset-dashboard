# API Reference Documentation

## Overview

The Asset Management API is a RESTful service built with FastAPI that provides endpoints for managing IT assets, synchronizing data with Snipe-IT, and retrieving analytics information.

## Base URL

```
Production: https://your-domain.com/api
Development: http://localhost:8000/api
```

## Authentication

Currently, the API does not require authentication. In production environments, consider implementing:

- API Key authentication
- JWT tokens
- OAuth 2.0

## Content Types

- **Request**: `application/json`
- **Response**: `application/json`

## Common Response Format

All API responses follow a consistent format:

```json
{
  "data": {},           // Response data (varies by endpoint)
  "message": "string",  // Success/error message
  "status": "success"   // Status indicator
}
```

## Error Responses

### Standard Error Format

```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | OK - Request successful |
| 201 | Created - Resource created successfully |
| 400 | Bad Request - Invalid request data |
| 404 | Not Found - Resource not found |
| 422 | Validation Error - Request validation failed |
| 500 | Internal Server Error - Server error |

## Endpoints

### Assets

#### GET `/api/assets`

Retrieves all assets from the database.

**Parameters:**
- `limit` (optional, integer): Number of assets to return (default: all)
- `offset` (optional, integer): Number of assets to skip (default: 0)
- `company` (optional, string): Filter by company
- `category` (optional, string): Filter by category
- `status` (optional, string): Filter by status
- `manufacturer` (optional, string): Filter by manufacturer

**Example Request:**
```bash
curl -X GET "https://your-domain.com/api/assets?company=Company%20A&limit=10"
```

**Example Response:**
```json
[
  {
    "id": 1,
    "asset_name": "Laptop-001",
    "asset_tag": "LT001",
    "model_no": "XPS-13",
    "model": "Dell XPS 13",
    "company": "Company A",
    "category": "Laptop",
    "manufacturer": "Dell",
    "serial": "ABC123456",
    "warranty": "3 Years",
    "warranty_expires": "2026-01-15",
    "location": "Office A",
    "department": "IT",
    "status": "Active",
    "created_at": "2024-01-15T10:30:00"
  },
  {
    "id": 2,
    "asset_name": "Desktop-001",
    "asset_tag": "DT001",
    "model_no": "OptiPlex-7090",
    "model": "Dell OptiPlex 7090",
    "company": "Company A",
    "category": "Desktop",
    "manufacturer": "Dell",
    "serial": "DEF789012",
    "warranty": "2 Years",
    "warranty_expires": "2025-06-15",
    "location": "Office B",
    "department": "Engineering",
    "status": "Active",
    "created_at": "2024-01-16T14:20:00"
  }
]
```

#### GET `/api/assets/{asset_id}`

Retrieves a specific asset by ID.

**Parameters:**
- `asset_id` (path, integer): The ID of the asset to retrieve

**Example Request:**
```bash
curl -X GET "https://your-domain.com/api/assets/1"
```

**Example Response:**
```json
{
  "id": 1,
  "asset_name": "Laptop-001",
  "asset_tag": "LT001",
  "model_no": "XPS-13",
  "model": "Dell XPS 13",
  "company": "Company A",
  "category": "Laptop",
  "manufacturer": "Dell",
  "serial": "ABC123456",
  "warranty": "3 Years",
  "warranty_expires": "2026-01-15",
  "location": "Office A",
  "department": "IT",
  "status": "Active",
  "created_at": "2024-01-15T10:30:00"
}
```

#### POST `/api/assets`

Creates a new asset.

**Request Body:**
```json
{
  "asset_name": "New Laptop",
  "asset_tag": "LT002",
  "model_no": "XPS-15",
  "model": "Dell XPS 15",
  "company": "Company B",
  "category": "Laptop",
  "manufacturer": "Dell",
  "serial": "XYZ987654",
  "warranty": "3 Years",
  "warranty_expires": "2027-01-15",
  "location": "Office C",
  "department": "Sales",
  "status": "Active"
}
```

**Example Request:**
```bash
curl -X POST "https://your-domain.com/api/assets" \
  -H "Content-Type: application/json" \
  -d '{
    "asset_name": "New Laptop",
    "asset_tag": "LT002",
    "model_no": "XPS-15",
    "model": "Dell XPS 15",
    "company": "Company B",
    "category": "Laptop",
    "manufacturer": "Dell",
    "serial": "XYZ987654",
    "warranty": "3 Years",
    "warranty_expires": "2027-01-15",
    "location": "Office C",
    "department": "Sales",
    "status": "Active"
  }'
```

**Example Response:**
```json
{
  "id": 3,
  "asset_name": "New Laptop",
  "asset_tag": "LT002",
  "model_no": "XPS-15",
  "model": "Dell XPS 15",
  "company": "Company B",
  "category": "Laptop",
  "manufacturer": "Dell",
  "serial": "XYZ987654",
  "warranty": "3 Years",
  "warranty_expires": "2027-01-15",
  "location": "Office C",
  "department": "Sales",
  "status": "Active",
  "created_at": "2024-01-17T09:15:00"
}
```

#### PUT `/api/assets/{asset_id}`

Updates an existing asset.

**Parameters:**
- `asset_id` (path, integer): The ID of the asset to update

**Request Body:** (same as POST, all fields optional)

**Example Request:**
```bash
curl -X PUT "https://your-domain.com/api/assets/1" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "Pending Rebuild",
    "location": "Repair Center"
  }'
```

**Example Response:**
```json
{
  "id": 1,
  "asset_name": "Laptop-001",
  "asset_tag": "LT001",
  "model_no": "XPS-13",
  "model": "Dell XPS 13",
  "company": "Company A",
  "category": "Laptop",
  "manufacturer": "Dell",
  "serial": "ABC123456",
  "warranty": "3 Years",
  "warranty_expires": "2026-01-15",
  "location": "Repair Center",
  "department": "IT",
  "status": "Pending Rebuild",
  "created_at": "2024-01-15T10:30:00"
}
```

#### DELETE `/api/assets/{asset_id}`

Deletes an asset.

**Parameters:**
- `asset_id` (path, integer): The ID of the asset to delete

**Example Request:**
```bash
curl -X DELETE "https://your-domain.com/api/assets/1"
```

**Example Response:**
```json
{
  "message": "Asset deleted successfully",
  "status": "success"
}
```

### Synchronization

#### POST `/api/sync`

Synchronizes assets from Snipe-IT API to the local database.

**Request Body:**
```json
{
  "force": false
}
```

**Parameters:**
- `force` (optional, boolean): Force full synchronization (default: false)

**Example Request:**
```bash
curl -X POST "https://your-domain.com/api/sync" \
  -H "Content-Type: application/json" \
  -d '{"force": true}'
```

**Example Response:**
```json
{
  "message": "Sync completed successfully",
  "assets_synced": 150,
  "assets_updated": 45,
  "assets_created": 5,
  "errors": [],
  "timestamp": "2024-01-17T10:30:00",
  "duration_seconds": 12.5
}
```

#### GET `/api/sync/status`

Retrieves the current synchronization status.

**Example Request:**
```bash
curl -X GET "https://your-domain.com/api/sync/status"
```

**Example Response:**
```json
{
  "last_sync": "2024-01-17T10:30:00",
  "sync_in_progress": false,
  "total_assets": 150,
  "last_sync_duration": 12.5,
  "last_sync_errors": [],
  "snipeit_connection": "healthy"
}
```

### Analytics

#### GET `/api/analytics/summary`

Retrieves summary analytics for the dashboard.

**Example Request:**
```bash
curl -X GET "https://your-domain.com/api/analytics/summary"
```

**Example Response:**
```json
{
  "total_assets": 150,
  "assets_by_status": {
    "Active": 120,
    "Pending Rebuild": 15,
    "Stock": 10,
    "Retired": 5
  },
  "assets_by_category": {
    "Laptop": 80,
    "Desktop": 45,
    "Monitor": 15,
    "Server": 10
  },
  "assets_by_company": {
    "Company A": 75,
    "Company B": 50,
    "Company C": 25
  },
  "warranty_expiring_soon": 8,
  "recent_additions": 12
}
```

#### GET `/api/analytics/trends`

Retrieves asset trends over time.

**Parameters:**
- `period` (optional, string): Time period (daily, weekly, monthly) (default: monthly)
- `start_date` (optional, string): Start date (YYYY-MM-DD)
- `end_date` (optional, string): End date (YYYY-MM-DD)

**Example Request:**
```bash
curl -X GET "https://your-domain.com/api/analytics/trends?period=monthly&start_date=2024-01-01&end_date=2024-12-31"
```

**Example Response:**
```json
{
  "period": "monthly",
  "data": [
    {
      "date": "2024-01",
      "assets_added": 15,
      "assets_retired": 3,
      "active_assets": 150
    },
    {
      "date": "2024-02",
      "assets_added": 8,
      "assets_retired": 2,
      "active_assets": 156
    }
  ]
}
```

#### GET `/api/analytics/warranty`

Retrieves warranty expiration analytics.

**Parameters:**
- `months_ahead` (optional, integer): Number of months to look ahead (default: 12)

**Example Request:**
```bash
curl -X GET "https://your-domain.com/api/analytics/warranty?months_ahead=6"
```

**Example Response:**
```json
{
  "months_ahead": 6,
  "expiring_assets": [
    {
      "id": 1,
      "asset_name": "Laptop-001",
      "asset_tag": "LT001",
      "warranty_expires": "2024-06-15",
      "days_until_expiry": 45,
      "company": "Company A",
      "category": "Laptop"
    }
  ],
  "summary": {
    "total_expiring": 8,
    "expiring_this_month": 2,
    "expiring_next_month": 3,
    "expiring_in_3_months": 3
  }
}
```

### Health Check

#### GET `/api/health`

Retrieves the health status of the API and its dependencies.

**Example Request:**
```bash
curl -X GET "https://your-domain.com/api/health"
```

**Example Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-17T10:30:00",
  "version": "1.0.0",
  "dependencies": {
    "database": "healthy",
    "snipeit_api": "healthy"
  },
  "uptime_seconds": 86400
}
```

## Data Models

### Asset Model

```json
{
  "id": "integer (optional)",
  "asset_name": "string (optional)",
  "asset_tag": "string (optional, unique)",
  "model_no": "string (optional)",
  "model": "string (optional)",
  "company": "string (optional)",
  "category": "string (optional)",
  "manufacturer": "string (optional)",
  "serial": "string (optional)",
  "warranty": "string (optional)",
  "warranty_expires": "date (optional, YYYY-MM-DD)",
  "location": "string (optional)",
  "department": "string (optional)",
  "status": "string (optional)",
  "created_at": "string (optional, ISO 8601)"
}
```

### Sync Request Model

```json
{
  "force": "boolean (optional, default: false)"
}
```

### Sync Response Model

```json
{
  "message": "string",
  "assets_synced": "integer",
  "assets_updated": "integer (optional)",
  "assets_created": "integer (optional)",
  "errors": "array (optional)",
  "timestamp": "string (ISO 8601)",
  "duration_seconds": "number (optional)"
}
```

## Rate Limiting

Currently, the API does not implement rate limiting. For production deployments, consider implementing:

- Request rate limiting per IP
- API key-based rate limiting
- Burst protection

## CORS Configuration

The API is configured to allow requests from specific origins:

```python
origins = [
    "http://10.4.208.227",
    "http://asset-ny.worldwide.bbc.co.uk"
]
```

## Error Handling

### Validation Errors

When request data fails validation:

```json
{
  "detail": [
    {
      "loc": ["body", "asset_tag"],
      "msg": "field required",
      "type": "value_error.missing"
    },
    {
      "loc": ["body", "warranty_expires"],
      "msg": "invalid date format",
      "type": "value_error.date"
    }
  ]
}
```

### Database Errors

When database operations fail:

```json
{
  "detail": "Database connection error",
  "error_code": "DB_CONNECTION_ERROR"
}
```

### Snipe-IT API Errors

When Snipe-IT synchronization fails:

```json
{
  "detail": "Failed to connect to Snipe-IT API",
  "error_code": "SNIPEIT_CONNECTION_ERROR",
  "retry_after": 300
}
```

## SDK Examples

### Python

```python
import requests

# Get all assets
response = requests.get("https://your-domain.com/api/assets")
assets = response.json()

# Create new asset
new_asset = {
    "asset_name": "New Asset",
    "asset_tag": "NA001",
    "company": "Company A",
    "category": "Laptop"
}
response = requests.post("https://your-domain.com/api/assets", json=new_asset)

# Sync with Snipe-IT
response = requests.post("https://your-domain.com/api/sync", json={"force": True})
```

### JavaScript

```javascript
// Get all assets
const response = await fetch('https://your-domain.com/api/assets');
const assets = await response.json();

// Create new asset
const newAsset = {
    asset_name: "New Asset",
    asset_tag: "NA001",
    company: "Company A",
    category: "Laptop"
};

const response = await fetch('https://your-domain.com/api/assets', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(newAsset)
});

// Sync with Snipe-IT
const syncResponse = await fetch('https://your-domain.com/api/sync', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({ force: true })
});
```

### cURL

```bash
# Get all assets
curl -X GET "https://your-domain.com/api/assets"

# Create new asset
curl -X POST "https://your-domain.com/api/assets" \
  -H "Content-Type: application/json" \
  -d '{"asset_name": "New Asset", "asset_tag": "NA001"}'

# Sync with Snipe-IT
curl -X POST "https://your-domain.com/api/sync" \
  -H "Content-Type: application/json" \
  -d '{"force": true}'

curl -X POST -d "" "http://asset-ny.worldwide.bbc.co.uk/api/sync/users"
curl -X POST -d "" "http://asset-ny.worldwide.bbc.co.uk/api/sync/all"
curl -X POST -d "" "http://asset-ny.worldwide.bbc.co.uk/api/sync/assets"
curl -X POST -d "" "http://asset-ny.worldwide.bbc.co.uk/api/sync/now"

curl "http://asset-ny.worldwide.bbc.co.uk/api/sync/schedule"
curl "http://asset-ny.worldwide.bbc.co.uk/api/users"
curl "http://asset-ny.worldwide.bbc.co.uk/api/assets"
```

## Versioning

The API currently uses version 1.0. Future versions will be available at:

```
https://your-domain.com/api/v2/
```

## Deprecation Policy

- Deprecated endpoints will be marked with a deprecation header
- Deprecated endpoints will continue to work for 12 months
- Migration guides will be provided for breaking changes

## Support

For API support and questions:

- **Documentation**: Available at `/docs` (Swagger UI)
- **Issues**: Report via GitHub issues
- **Email**: api-support@your-domain.com 