# API Documentation

Base URL: `/api/v1/`  
All endpoints return JSON. Authentication uses Django session or token (DRF).

---

## Analytics

### GET `/analytics/data/`

Returns all chart data for the analytics dashboard.

**Query Parameters**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `village` | string | `all` | Village slug or `all` |

**Response** (abbreviated)
```json
{
  "village_comparison": [{"village": "Maharajupeta", "total": 42, "internet_users": 30}],
  "age_vs_internet": {"categories": ["18-25", "26-35", ...], "internet_yes": [12, 8, ...], "internet_no": [3, 5, ...]},
  "device_distribution": [{"name": "Smartphone", "value": 58}],
  "daily_trend": {"dates": ["2025-06-01", ...], "counts": [5, 8, ...]},
  "awareness_heatmap": {"villages": [...], "age_groups": [...], "data": [[0,0,3.2], ...]},
  ...
}
```

### GET `/analytics/insights/`

Returns auto-generated textual insights.

```json
{
  "insights": [
    {"title": "High Fraud Risk", "text": "...", "severity": "danger", "icon": "⚠️"},
    ...
  ]
}
```

---

## Survey

### GET `/api/v1/surveys/`

List survey responses (paginated). Requires auth.

### POST `/api/v1/surveys/`

Submit a survey response.

**Body (JSON)**
```json
{
  "village": 1,
  "respondent_name": "optional",
  "age_group": "26-35",
  "gender": "F",
  "education": "degree",
  "occupation": "farmer",
  "uses_internet": true,
  "devices": ["smartphone"],
  "internet_purposes": ["social", "banking"],
  "connection_type": "mobile_4g",
  "hours_per_day": "1-3",
  "knows_otp_rule": true,
  "experienced_fraud": "no",
  "uses_strong_passwords": "sometimes",
  "knows_phishing": "yes",
  "checks_https": "yes"
}
```

---

## Villages

### GET `/api/v1/villages/`

List all active villages.

### GET `/api/v1/villages/<slug>/`

Detail for a single village including computed survey stats.

### GET `/villages/map-data/`

Returns GeoJSON-compatible list of villages with coordinates.
```json
[{"id": 1, "name": "Maharajupeta", "lat": 18.112, "lng": 83.395, "color": "#06B6D4", "survey_count": 42, "url": "/villages/maharajupeta/"}]
```

---

## Gallery

### GET `/gallery/data/`

Returns filtered photo list (max 200).

**Query Parameters**: `village`, `category`, `q` (search term)

---

## AI Assistant

### POST `/ai/api/chat/`

Submit a question to the RAG-powered AI assistant.

**Body (JSON)**
```json
{"question": "Which village has the highest awareness score?"}
```

**Response**
```json
{
  "answer": "Based on the survey data, Maharajupeta has the highest...",
  "sources": ["villages", "surveys"],
  "error": null
}
```

### GET `/ai/api/suggested/`

Returns list of suggested questions.

### POST `/ai/api/rebuild/`

Rebuild the ChromaDB knowledge base. Requires `is_staff=true`.

---

## Search

### GET `/search/?q=<term>`

Returns results from villages, visits, and team members.

```json
{
  "villages": [{"name": "Maharajupeta", "url": "/villages/maharajupeta/"}],
  "visits": [{"title": "Day 1 Visit", "url": "/visits/1/"}],
  "team": [{"name": "Alice", "url": "/team/#alice"}]
}
```
