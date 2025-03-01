# Photo Editing API

A FastAPI-based REST API for editing images with layer support and shape drawing capabilities.

## Features

- Create and manage photo editing projects
- Add and manipulate image layers
- Draw shapes (rectangles, circles, arcs)
- Export projects as PNG or JPEG
- Secure API access

## Quick Start

1. Clone the repository and install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your configuration:
```
SECRET_KEY="your-secret-key-here"
ADMIN_API_KEY="your-admin-token-here"
```

3. Run the development server:
```bash
uvicorn app.main:app --reload
```

4. Access the API at `http://localhost:8000`

## API Documentation

View the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Authentication

All API requests require an API key passed in the `X-API-Key` header.

## Basic Usage

```bash
# Create a new project
curl -X POST http://localhost:8000/api/v1/projects \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Project", "description": "Test project"}'

# Add a shape to the project
curl -X POST http://localhost:8000/api/v1/projects/{project_id}/layers/rectangle \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"x": 10, "y": 10, "width": 100, "height": 100, "color": "#FF0000"}'
```

## AI Use
Commit messages
Generating README.md 