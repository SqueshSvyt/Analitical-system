# API Reference

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication. In production, implement proper authentication.

## Response Format

All responses are in JSON format. Successful responses return data directly or in a structured format. Error responses follow this structure:

```json
{
  "detail": "Error message"
}
```

---

## Event Monitor API

### Get Events

Retrieve filtered list of events.

**Endpoint:** `POST /analytics/events`

**Request Body:**
```json
{
  "start_date": "2024-01-01T00:00:00Z",
  "end_date": "2024-12-31T23:59:59Z",
  "event_types": ["Conflict.Attack", "Diplomacy"],
  "entities": ["Russia", "Ukraine"],
  "sources": ["Reuters", "BBC"],
  "min_confidence": 0.7,
  "limit": 50
}
```

**Response:**
```json
[
  {
    "event_id": "evt_123",
    "type": "Conflict.Attack",
    "trigger_word": "attacked",
    "confidence": 0.85,
    "article_id": "art_456",
    "article_title": "Breaking News...",
    "published_date": "2024-06-15T10:30:00Z",
    "entities": ["Russia", "Ukraine", "Kiev"]
  }
]
```

### Get Event Trends

Get time-series data of events.

**Endpoint:** `GET /analytics/events/trends`

**Query Parameters:**
- `start_date` (optional): ISO datetime
- `end_date` (optional): ISO datetime
- `event_types` (optional): List of event types
- `granularity`: day | week | month (default: day)

**Response:**
```json
[
  {
    "date": "2024-06-15",
    "event_type": "Conflict.Attack",
    "count": 12
  }
]
```

### Get Top Actors

Get most frequent entities in events.

**Endpoint:** `GET /analytics/events/top-actors`

**Query Parameters:**
- `event_type` (optional): Filter by event type
- `start_date` (optional): ISO datetime
- `end_date` (optional): ISO datetime
- `limit` (optional): Number of results (default: 20)

**Response:**
```json
[
  {
    "entity_id": "ent_789",
    "text": "Russia",
    "label": "GPE",
    "event_count": 145,
    "event_types": ["Conflict.Attack", "Diplomacy.Sanction"]
  }
]
```

---

## Entity Intelligence API

### Search Entities

Search for entities by text pattern.

**Endpoint:** `POST /analytics/entities/search`

**Request Body:**
```json
{
  "query": "Russia",
  "label": "GPE",
  "limit": 50
}
```

**Response:**
```json
[
  {
    "entity_id": "ent_789",
    "text": "Russia",
    "label": "GPE",
    "event_count": 145
  }
]
```

### Get Entity Overview

Get comprehensive entity profile.

**Endpoint:** `GET /analytics/entities/{entity_id}/overview`

**Response:**
```json
{
  "entity_id": "ent_789",
  "text": "Russia",
  "label": "GPE",
  "total_events": 145,
  "event_distribution": {
    "Conflict.Attack": 50,
    "Diplomacy.Sanction": 45,
    "Diplomacy.Meeting": 30
  },
  "first_seen": "2024-01-01T00:00:00Z",
  "last_seen": "2024-12-20T15:30:00Z"
}
```

### Get Entity Timeline

Get chronological events involving entity.

**Endpoint:** `GET /analytics/entities/{entity_id}/timeline`

**Query Parameters:**
- `start_date` (optional): ISO datetime
- `end_date` (optional): ISO datetime
- `limit` (optional): Number of results (default: 100)

**Response:**
```json
[
  {
    "event_id": "evt_123",
    "event_type": "Conflict.Attack",
    "date": "2024-06-15T10:30:00Z",
    "article_title": "Breaking News...",
    "confidence": 0.85
  }
]
```

### Get Entity Network

Get k-hop network of related entities.

**Endpoint:** `GET /analytics/entities/{entity_id}/network`

**Query Parameters:**
- `k_hops`: 1-3 (default: 2)
- `limit`: Number of nodes (default: 50)

**Response:**
```json
{
  "nodes": [
    {
      "entity_id": "ent_456",
      "text": "Ukraine",
      "label": "GPE",
      "connection_count": 45
    }
  ],
  "edges": [
    {
      "source": "ent_789",
      "target": "ent_456",
      "event_id": "evt_123",
      "event_type": "Conflict.Attack",
      "weight": 45
    }
  ]
}
```

---

## Storyline Explorer API

### Find Storylines

Find event chains matching a pattern.

**Endpoint:** `POST /analytics/storylines/find`

**Request Body:**
```json
{
  "event_pattern": ["Conflict.Attack", "Diplomacy.Sanction", "Diplomacy.Meeting"],
  "start_date": "2024-01-01T00:00:00Z",
  "end_date": "2024-12-31T23:59:59Z",
  "max_days_between_events": 30,
  "limit": 20
}
```

**Response:**
```json
[
  {
    "chain_id": "chain_123",
    "events": [
      {
        "event_id": "evt_1",
        "type": "Conflict.Attack",
        "trigger_word": "attacked",
        "confidence": 0.85,
        "date": "2024-06-01T10:00:00Z",
        "article_title": "...",
        "article_id": "art_1"
      }
    ],
    "entities": ["Russia", "Ukraine"],
    "confidence": 0.82,
    "time_span_days": 25
  }
]
```

### Find Bridge Actors

Find entities connecting two event types.

**Endpoint:** `GET /analytics/bridge-actors`

**Query Parameters:**
- `event_type1`: First event type (required)
- `event_type2`: Second event type (required)
- `start_date` (optional): ISO datetime
- `end_date` (optional): ISO datetime
- `limit` (optional): Number of results (default: 20)

**Response:**
```json
[
  {
    "entity_id": "ent_789",
    "text": "Russia",
    "label": "GPE",
    "type1_events": 45,
    "type2_events": 30,
    "total_events": 75,
    "type1_examples": ["Conflict.Attack", "Conflict.AirStrike"],
    "type2_examples": ["Diplomacy.Sanction", "Diplomacy.Meeting"]
  }
]
```

---

## Alerts API

### Get Alerts

Get all alerts or filter by type.

**Endpoint:** `GET /analytics/alerts`

**Query Parameters:**
- `start_date` (optional): ISO datetime
- `end_date` (optional): ISO datetime
- `alert_type` (optional): spike | escalation | novelty | evidence

**Response:**
```json
[
  {
    "alert_id": "alert_123",
    "alert_type": "spike",
    "severity": "high",
    "title": "Spike in Conflict.Attack events",
    "description": "Detected 3.5x increase...",
    "triggered_at": "2024-06-15T10:30:00Z",
    "related_events": ["evt_1", "evt_2"],
    "related_entities": ["ent_789"],
    "supporting_articles": ["art_1", "art_2"]
  }
]
```

---

## Q&A API

### Ask Question

Submit analytical query and get fact-backed answer.

**Endpoint:** `POST /analytics/qa`

**Request Body:**
```json
{
  "query": "What events involve Russia and Ukraine?",
  "start_date": "2024-01-01T00:00:00Z",
  "end_date": "2024-12-31T23:59:59Z"
}
```

**Response:**
```json
{
  "query": "What events involve Russia and Ukraine?",
  "answer": "Found 145 events involving both Russia and Ukraine...",
  "evidence": [
    {
      "event_id": "evt_123",
      "event_type": "Conflict.Attack",
      "trigger_word": "attacked",
      "confidence": 0.85,
      "article": {
        "article_id": "art_456",
        "title": "Breaking News...",
        "published_date": "2024-06-15T10:30:00Z",
        "source": "Reuters",
        "link": "https://..."
      }
    }
  ],
  "related_entities": ["ent_789", "ent_456"],
  "related_events": ["evt_123", "evt_124"]
}
```

---

## Statistics API

### Get Overview Statistics

Get overall knowledge graph statistics.

**Endpoint:** `GET /analytics/stats/overview`

**Response:**
```json
{
  "total_articles": 10000,
  "total_events": 25000,
  "total_entities": 5000,
  "date_range": {
    "earliest": "2024-01-01T00:00:00Z",
    "latest": "2024-12-20T15:30:00Z"
  }
}
```

### Get Event Type Distribution

Get counts by event type.

**Endpoint:** `GET /analytics/stats/event-types`

**Response:**
```json
[
  {
    "event_type": "Conflict.Attack",
    "count": 5000
  },
  {
    "event_type": "Diplomacy.Sanction",
    "count": 3000
  }
]
```

---

## Error Codes

- `400` - Bad Request: Invalid input parameters
- `404` - Not Found: Resource not found
- `422` - Unprocessable Entity: Validation error
- `500` - Internal Server Error: Server error
- `503` - Service Unavailable: Database connection failed

## Rate Limiting

Currently no rate limiting is implemented. For production, implement rate limiting based on your requirements.

## Pagination

For endpoints returning large datasets, use the `limit` parameter. Future versions may implement cursor-based pagination.

