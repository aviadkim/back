# Avi Feature

## Overview
Avi feature implementation.

## Structure
```
avi/
├── api/                # Backend API files
│   ├── routes.js       # API endpoints
│   ├── controller.js   # Request handlers
│   └── service.js      # Business logic
├── components/         # Frontend components
│   ├── Avi.jsx  # Main component
│   └── styles.css      # Component styles
├── tests/              # Test files
│   ├── Avi.test.js  # Frontend tests
│   └── api.test.js     # API tests
└── index.js            # Feature exports
```

## Usage
```jsx
import { Avi } from './features/avi';

// Then use in your app
<Avi />
```

## API Endpoints
- `GET /api/avi` - Get all items
- `GET /api/avi/:id` - Get item by ID
- `POST /api/avi` - Create new item
- `PUT /api/avi/:id` - Update item
- `DELETE /api/avi/:id` - Delete item
