# GreenRank API Documentation

> **Version:** 1.0  
> **Base URL:** `http://localhost:5000/api`  
> **Last Updated:** November 2025

REST API for sustainability scoring of 290 UK companies across 5 sectors with 21 environmental metrics.

---

## Table of Contents

- [Authentication](#authentication)
- [Base URL](#base-url)
- [Response Format](#response-format)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Endpoints](#endpoints)
  - [System](#system)
  - [Sectors](#sectors)
  - [Metrics](#metrics)
  - [Companies](#companies)
  - [Scores](#scores)
- [Data Models](#data-models)
- [Code Examples](#code-examples)
- [Changelog](#changelog)

---

## Authentication

Currently, this API does not require authentication. All endpoints are publicly accessible.

**Note:** For production deployment, implement API key authentication or OAuth2.

---

## Base URL

All API requests should be made to:

```
http://localhost:5000/api
```

**Production:** Replace with your deployed domain.

---

## Response Format

All responses are returned in JSON format with appropriate HTTP status codes.

### Success Response

```json
{
  "data": { ... },
  "status": "success"
}
```

### Error Response

```json
{
  "error": "Error message description",
  "status": "error"
}
```

---

## Error Handling

The API uses standard HTTP status codes:

| Status Code | Meaning |
|-------------|---------|
| `200` | Success |
| `404` | Resource not found |
| `500` | Internal server error |

---

## Rate Limiting

Currently no rate limiting is implemented.

**Production Recommendation:** Implement rate limiting (e.g., 100 requests/minute per IP).

---

## Endpoints

### System

#### Health Check

Check API and database connectivity status.

```http
GET /api/health
```

**Response:**

```json
{
  "status": "healthy",
  "database": "connected"
}
```

**Example:**

```javascript
fetch('http://localhost:5000/api/health')
  .then(res => res.json())
  .then(data => console.log(data.status));
```

---

#### Get Statistics

Retrieve overall system statistics.

```http
GET /api/stats
```

**Response:**

```json
{
  "total_companies": 290,
  "total_sectors": 5,
  "total_metrics": 21,
  "companies_scored": 290,
  "last_updated": "2025-11-12T00:45:23.123456"
}
```

**Example:**

```javascript
fetch('http://localhost:5000/api/stats')
  .then(res => res.json())
  .then(stats => {
    console.log(`Companies: ${stats.total_companies}`);
    console.log(`Last Updated: ${new Date(stats.last_updated).toLocaleString()}`);
  });
```

---

### Sectors

#### List All Sectors

Retrieve all available sectors.

```http
GET /api/sectors
```

**Response:**

```json
[
  {
    "id": 1,
    "sector_name": "finance",
    "description": ""
  },
  {
    "id": 2,
    "sector_name": "retail",
    "description": ""
  },
  {
    "id": 3,
    "sector_name": "fashion",
    "description": ""
  },
  {
    "id": 4,
    "sector_name": "heavy industry",
    "description": ""
  },
  {
    "id": 5,
    "sector_name": "construction",
    "description": ""
  }
]
```

**Example:**

```javascript
fetch('http://localhost:5000/api/sectors')
  .then(res => res.json())
  .then(sectors => {
    sectors.forEach(sector => {
      console.log(`${sector.id}: ${sector.sector_name}`);
    });
  });
```

---

#### Get Single Sector

Retrieve detailed information about a specific sector including its metrics.

```http
GET /api/sectors/{id}
```

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | integer | Yes | Sector ID (1-5) |

**Response:**

```json
{
  "id": 2,
  "sector_name": "retail",
  "description": "",
  "metrics": [
    {
      "sector_metric_id": 6,
      "sector_id": 2,
      "metric_id": 1,
      "weight": 0.1
    },
    {
      "sector_metric_id": 7,
      "sector_id": 2,
      "metric_id": 2,
      "weight": 0.1
    }
    // ... more metrics
  ]
}
```

**Example:**

```javascript
const sectorId = 2;
fetch(`http://localhost:5000/api/sectors/${sectorId}`)
  .then(res => res.json())
  .then(sector => {
    console.log(`Sector: ${sector.sector_name}`);
    console.log(`Metrics: ${sector.metrics.length}`);
  });
```

---

#### Get Sector Leaderboard

Retrieve ranked companies within a specific sector.

```http
GET /api/sectors/{id}/leaderboard
```

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | integer | Yes | Sector ID (1-5) |

**Response:**

```json
{
  "sector_id": 2,
  "sector_name": "retail",
  "companies": [
    {
      "rank": 1,
      "company_id": 4,
      "name": "Tesco",
      "sector_id": 2,
      "sector_name": "retail",
      "turnover": 88.08,
      "country": "UK",
      "description": "",
      "website": "",
      "sector_score": 87.32,
      "global_score": 99.7,
      "last_calculated": "2025-11-12T00:45:23"
    }
    // ... more companies
  ]
}
```

**Example:**

```javascript
fetch('http://localhost:5000/api/sectors/2/leaderboard')
  .then(res => res.json())
  .then(data => {
    console.log(`${data.sector_name} Leaderboard`);
    data.companies.forEach(company => {
      console.log(`${company.rank}. ${company.name} - ${company.sector_score.toFixed(2)}`);
    });
  });
```

---

### Metrics

#### List All Metrics

Retrieve all sustainability metrics.

```http
GET /api/metrics
```

**Response:**

```json
[
  {
    "metric_id": 1,
    "metric_name": "Operational_energy",
    "unit": "MWh/Year",
    "invert_score": false,
    "description": "Operational energy use consumed by offices and data centres each year",
    "source": ""
  },
  {
    "metric_id": 2,
    "metric_name": "Renewable_energy_percent",
    "unit": "%",
    "invert_score": false,
    "description": "Renewable energy % per year",
    "source": ""
  }
  // ... 19 more metrics
]
```

**Example:**

```javascript
fetch('http://localhost:5000/api/metrics')
  .then(res => res.json())
  .then(metrics => {
    metrics.forEach(metric => {
      console.log(`${metric.metric_name} (${metric.unit})`);
    });
  });
```

---

#### Get Single Metric

Retrieve details about a specific metric.

```http
GET /api/metrics/{id}
```

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | integer | Yes | Metric ID (1-21) |

**Response:**

```json
{
  "metric_id": 2,
  "metric_name": "Renewable_energy_percent",
  "unit": "%",
  "invert_score": false,
  "description": "Renewable energy % per year",
  "source": ""
}
```

**Example:**

```javascript
const metricId = 2;
fetch(`http://localhost:5000/api/metrics/${metricId}`)
  .then(res => res.json())
  .then(metric => {
    console.log(`${metric.metric_name}: ${metric.description}`);
  });
```

---

### Companies

#### List All Companies

Retrieve a list of companies with optional filtering and pagination.

```http
GET /api/companies
```

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `sector_id` | integer | No | - | Filter by sector (1-5) |
| `limit` | integer | No | 100 | Number of results to return |
| `offset` | integer | No | 0 | Number of results to skip |

**Response:**

```json
{
  "total": 290,
  "limit": 100,
  "offset": 0,
  "companies": [
    {
      "company_id": 1,
      "name": "Shell",
      "sector_id": 4,
      "sector_name": "heavy industry",
      "turnover": 272.01,
      "country": "UK",
      "description": "",
      "website": "",
      "sector_score": 45.23,
      "global_score": 32.1,
      "last_calculated": "2025-11-12T00:45:23"
    }
    // ... more companies
  ]
}
```

**Examples:**

```javascript
// Get all companies
fetch('http://localhost:5000/api/companies')
  .then(res => res.json())
  .then(data => console.log(`Total: ${data.total} companies`));

// Filter by sector
fetch('http://localhost:5000/api/companies?sector_id=2')
  .then(res => res.json())
  .then(data => console.log(`Retail companies: ${data.companies.length}`));

// Pagination
fetch('http://localhost:5000/api/companies?limit=50&offset=50')
  .then(res => res.json())
  .then(data => console.log('Next 50 companies:', data.companies));

// Combined filters
fetch('http://localhost:5000/api/companies?sector_id=1&limit=20')
  .then(res => res.json())
  .then(data => console.log('Top 20 finance companies:', data.companies));
```

---

#### Get Single Company

Retrieve detailed information about a specific company including all sustainability metrics.

```http
GET /api/companies/{id}
```

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | integer | Yes | Company ID (1-290) |

**Response:**

```json
{
  "company_id": 4,
  "name": "Tesco",
  "sector_id": 2,
  "sector_name": "retail",
  "turnover": 88.08,
  "country": "UK",
  "description": "",
  "website": "",
  "sector_score": 87.32,
  "global_score": 99.7,
  "last_calculated": "2025-11-12T00:45:23",
  "metrics": [
    {
      "metric_id": 1,
      "metric_name": "Operational_energy",
      "value": 1650000.0,
      "unit": "MWh/Year",
      "year": 2023
    },
    {
      "metric_id": 2,
      "metric_name": "Renewable_energy_percent",
      "value": 100.0,
      "unit": "%",
      "year": 2023
    },
    {
      "metric_id": 3,
      "metric_name": "C02_emissions_yearly",
      "value": 1094000.0,
      "unit": "tCO2e",
      "year": 2023
    }
    // ... more metrics
  ]
}
```

**Example:**

```javascript
const companyId = 4; // Tesco
fetch(`http://localhost:5000/api/companies/${companyId}`)
  .then(res => res.json())
  .then(company => {
    console.log(`Company: ${company.name}`);
    console.log(`Sector: ${company.sector_name}`);
    console.log(`Score: ${company.sector_score.toFixed(2)}`);
    console.log(`Global Rank: Top ${company.global_score.toFixed(1)}%`);
    
    // Display metrics
    company.metrics.forEach(metric => {
      console.log(`${metric.metric_name}: ${metric.value} ${metric.unit}`);
    });
  });
```

---

#### Search Companies

Search for companies by name (case-insensitive).

```http
GET /api/companies/search
```

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `q` | string | Yes | Search query (minimum 1 character) |

**Response:**

```json
{
  "query": "tesco",
  "count": 1,
  "companies": [
    {
      "company_id": 4,
      "name": "Tesco",
      "sector_id": 2,
      "sector_name": "retail",
      "turnover": 88.08,
      "country": "UK",
      "description": "",
      "website": "",
      "sector_score": 87.32,
      "global_score": 99.7,
      "last_calculated": "2025-11-12T00:45:23"
    }
  ]
}
```

**Example:**

```javascript
// Basic search
const query = 'tesco';
fetch(`http://localhost:5000/api/companies/search?q=${query}`)
  .then(res => res.json())
  .then(data => {
    console.log(`Found ${data.count} companies matching "${data.query}"`);
    data.companies.forEach(company => {
      console.log(`- ${company.name}`);
    });
  });

// Search with user input
const searchInput = document.getElementById('search');
searchInput.addEventListener('input', (e) => {
  const query = e.target.value;
  if (query.length >= 2) {
    fetch(`http://localhost:5000/api/companies/search?q=${encodeURIComponent(query)}`)
      .then(res => res.json())
      .then(data => displaySearchResults(data.companies));
  }
});
```

---

### Scores

#### Get Global Leaderboard

Retrieve the top-ranked companies across all sectors.

```http
GET /api/leaderboard
```

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `limit` | integer | No | 50 | Number of results (1-100) |

**Response:**

```json
[
  {
    "rank": 1,
    "company_id": 4,
    "name": "Tesco",
    "sector_id": 2,
    "sector_name": "retail",
    "sector_score": 87.32,
    "global_score": 99.7,
    "turnover": 88.08
  },
  {
    "rank": 2,
    "company_id": 9,
    "name": "Sainsbury's",
    "sector_id": 2,
    "sector_name": "retail",
    "sector_score": 85.15,
    "global_score": 98.3,
    "turnover": 41.33
  }
  // ... more companies
]
```

**Examples:**

```javascript
// Get top 10 companies
fetch('http://localhost:5000/api/leaderboard?limit=10')
  .then(res => res.json())
  .then(companies => {
    console.log('🏆 Top 10 Sustainable Companies:');
    companies.forEach(company => {
      console.log(`${company.rank}. ${company.name} - Score: ${company.sector_score.toFixed(2)}`);
    });
  });

// Get top 100
fetch('http://localhost:5000/api/leaderboard?limit=100')
  .then(res => res.json())
  .then(companies => console.log('Top 100:', companies));
```

---

#### Get All Scores

Retrieve all computed sustainability scores.

```http
GET /api/scores
```

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `limit` | integer | No | - | Limit number of results |

**Response:**

```json
[
  {
    "rank": 1,
    "score_id": 4,
    "company_id": 4,
    "company_name": "Tesco",
    "sector_score": 87.32,
    "global_score": 99.7,
    "last_calculated": "2025-11-12T00:45:23"
  }
  // ... more scores
]
```

**Example:**

```javascript
fetch('http://localhost:5000/api/scores?limit=20')
  .then(res => res.json())
  .then(scores => {
    scores.forEach(score => {
      console.log(`${score.rank}. ${score.company_name}: ${score.sector_score}`);
    });
  });
```

---

## Data Models

### Sector

```typescript
interface Sector {
  id: number;
  sector_name: string;
  description: string;
}
```

### Metric

```typescript
interface Metric {
  metric_id: number;
  metric_name: string;
  unit: string;
  invert_score: boolean;
  description: string;
  source: string;
}
```

### Company

```typescript
interface Company {
  company_id: number;
  name: string;
  sector_id: number;
  sector_name: string;
  turnover: number;
  country: string;
  description: string;
  website: string;
  sector_score?: number;
  global_score?: number;
  last_calculated?: string;
}
```

### CompanyDetailed

```typescript
interface CompanyDetailed extends Company {
  metrics: CompanyMetric[];
}

interface CompanyMetric {
  metric_id: number;
  metric_name: string;
  value: number;
  unit: string;
  year: number;
}
```

### Score

```typescript
interface Score {
  score_id: number;
  company_id: number;
  company_name: string;
  sector_score: number;
  global_score: number;
  last_calculated: string;
}
```

---

## Code Examples

### React Component - Leaderboard

```jsx
import { useState, useEffect } from 'react';

function Leaderboard() {
  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('http://localhost:5000/api/leaderboard?limit=10')
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch');
        return res.json();
      })
      .then(data => {
        setCompanies(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="leaderboard">
      <h1>🏆 Top 10 Sustainable Companies</h1>
      <table>
        <thead>
          <tr>
            <th>Rank</th>
            <th>Company</th>
            <th>Sector</th>
            <th>Score</th>
          </tr>
        </thead>
        <tbody>
          {companies.map(company => (
            <tr key={company.company_id}>
              <td>{company.rank}</td>
              <td>{company.name}</td>
              <td>{company.sector_name}</td>
              <td>{company.sector_score.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default Leaderboard;
```

---

### React Component - Company Detail

```jsx
import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';

function CompanyDetail() {
  const { id } = useParams();
  const [company, setCompany] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`http://localhost:5000/api/companies/${id}`)
      .then(res => res.json())
      .then(data => {
        setCompany(data);
        setLoading(false);
      });
  }, [id]);

  if (loading) return <div>Loading...</div>;
  if (!company) return <div>Company not found</div>;

  return (
    <div className="company-detail">
      <h1>{company.name}</h1>
      
      <div className="company-info">
        <p><strong>Sector:</strong> {company.sector_name}</p>
        <p><strong>Turnover:</strong> £{company.turnover}B</p>
        <p><strong>Country:</strong> {company.country}</p>
        <p><strong>Sustainability Score:</strong> {company.sector_score.toFixed(2)}/100</p>
        <p><strong>Global Ranking:</strong> Top {company.global_score.toFixed(1)}%</p>
      </div>

      <h2>Sustainability Metrics</h2>
      <div className="metrics-grid">
        {company.metrics.map(metric => (
          <div key={metric.metric_id} className="metric-card">
            <h3>{metric.metric_name}</h3>
            <p className="metric-value">
              {metric.value} <span className="unit">{metric.unit}</span>
            </p>
            <p className="metric-year">Year: {metric.year}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default CompanyDetail;
```

---

### React Component - Search

```jsx
import { useState, useEffect } from 'react';

function CompanySearch() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (query.length < 2) {
      setResults([]);
      return;
    }

    setLoading(true);
    const timeoutId = setTimeout(() => {
      fetch(`http://localhost:5000/api/companies/search?q=${encodeURIComponent(query)}`)
        .then(res => res.json())
        .then(data => {
          setResults(data.companies);
          setLoading(false);
        });
    }, 300); // Debounce

    return () => clearTimeout(timeoutId);
  }, [query]);

  return (
    <div className="search-container">
      <input
        type="text"
        placeholder="Search companies..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        className="search-input"
      />
      
      {loading && <div>Searching...</div>}
      
      {results.length > 0 && (
        <ul className="search-results">
          {results.map(company => (
            <li key={company.company_id}>
              <a href={`/companies/${company.company_id}`}>
                <strong>{company.name}</strong>
                <span className="sector">{company.sector_name}</span>
                <span className="score">
                  Score: {company.sector_score?.toFixed(2) || 'N/A'}
                </span>
              </a>
            </li>
          ))}
        </ul>
      )}
      
      {query.length >= 2 && results.length === 0 && !loading && (
        <div className="no-results">No companies found</div>
      )}
    </div>
  );
}

export default CompanySearch;
```

---

### Axios Service Layer

```javascript
// services/api.js
import axios from 'axios';

const API = axios.create({
  baseURL: 'http://localhost:5000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add response interceptor for error handling
API.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export const api = {
  // Health
  healthCheck: () => API.get('/health'),
  
  // Stats
  getStats: () => API.get('/stats'),
  
  // Sectors
  getSectors: () => API.get('/sectors'),
  getSector: (id) => API.get(`/sectors/${id}`),
  getSectorLeaderboard: (id) => API.get(`/sectors/${id}/leaderboard`),
  
  // Metrics
  getMetrics: () => API.get('/metrics'),
  getMetric: (id) => API.get(`/metrics/${id}`),
  
  // Companies
  getCompanies: (params = {}) => API.get('/companies', { params }),
  getCompany: (id) => API.get(`/companies/${id}`),
  searchCompanies: (query) => API.get('/companies/search', { params: { q: query } }),
  
  // Scores
  getLeaderboard: (limit = 50) => API.get('/leaderboard', { params: { limit } }),
  getScores: (limit) => API.get('/scores', { params: { limit } })
};

// Usage example:
// import { api } from './services/api';
// const response = await api.getLeaderboard(10);
// console.log(response.data);
```

---

### Vue.js Composition API

```vue
<template>
  <div class="leaderboard">
    <h1>Top Companies</h1>
    
    <div v-if="loading">Loading...</div>
    <div v-else-if="error">Error: {{ error }}</div>
    
    <ul v-else>
      <li v-for="company in companies" :key="company.company_id">
        {{ company.rank }}. {{ company.name }} - {{ company.sector_score.toFixed(2) }}
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const companies = ref([]);
const loading = ref(true);
const error = ref(null);

onMounted(async () => {
  try {
    const response = await fetch('http://localhost:5000/api/leaderboard?limit=10');
    if (!response.ok) throw new Error('Failed to fetch');
    companies.value = await response.json();
  } catch (e) {
    error.value = e.message;
  } finally {
    loading.value = false;
  }
});
</script>
```

---

### Vanilla JavaScript

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>GreenRank Leaderboard</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; }
    .company { padding: 10px; border-bottom: 1px solid #ddd; }
    .rank { font-weight: bold; }
    .score { color: #28a745; float: right; }
  </style>
</head>
<body>
  <h1>🏆 Top 10 Sustainable Companies</h1>
  <div id="leaderboard">Loading...</div>

  <script>
    async function loadLeaderboard() {
      try {
        const response = await fetch('http://localhost:5000/api/leaderboard?limit=10');
        const companies = await response.json();
        
        const html = companies.map(c => `
          <div class="company">
            <span class="rank">${c.rank}. ${c.name}</span>
            <span class="score">${c.sector_score.toFixed(2)}</span>
          </div>
        `).join('');
        
        document.getElementById('leaderboard').innerHTML = html;
      } catch (error) {
        document.getElementById('leaderboard').innerHTML = 
          `<p>Error loading data: ${error.message}</p>`;
      }
    }

    loadLeaderboard();
  </script>
</body>
</html>
```

---

## Changelog

### Version 1.0 (November 2025)

**Initial Release**

- 15 REST API endpoints
- 290 UK companies across 5 sectors
- 21 sustainability metrics
- Z-score normalization scoring algorithm
- PostgreSQL database with 2,192 data points
- CORS enabled for development
- Full JSON response format

**Endpoints Added:**
- System: `/health`, `/stats`
- Sectors: `/sectors`, `/sectors/:id`, `/sectors/:id/leaderboard`
- Metrics: `/metrics`, `/metrics/:id`
- Companies: `/companies`, `/companies/:id`, `/companies/search`
- Scores: `/leaderboard`, `/scores`

---

## Support

For questions or issues:
- Check the main `README.md` for setup instructions
- Review `SETUP_GUIDE.md` for troubleshooting
- Contact the development team

---

## License

[Your License Here]

---

**Last Updated:** November 12, 2025  
**Maintained by:** [Your Team Name]
