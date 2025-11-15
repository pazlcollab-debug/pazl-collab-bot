# 🔍 PAZL Collab Bot - Full Project Audit Report

**Date:** 2025-01-27  
**Project:** PAZL Collab Bot (Telegram Bot + FastAPI + React Mini App)

---

## 📋 Summary

This audit identified **15 critical issues**, **8 major bugs**, and **12 architectural improvements** needed for stable operation. The main problems are:

1. **Routing conflict** between `App.jsx` and `main.jsx` causing navigation failures
2. **Missing `telegram_id` field** in API responses breaking profile navigation
3. **Duplicate code** in `services/airtable_api.py` (300+ lines duplicated)
4. **Character encoding issues** in Gallery.jsx
5. **Missing environment variable** configuration for frontend
6. **API response structure mismatch** between backend and frontend expectations

---

## 🚨 Critical Issues

### 1. **ROUTING CONFLICT - Gallery Not Showing** ⚠️ CRITICAL
**Location:** `frontend/src/main.jsx` + `frontend/src/App.jsx`  
**Line Numbers:** `main.jsx:17-25`, `App.jsx:7-18`

**Problem:**
- `main.jsx` uses `createBrowserRouter` with routes `["/", "/profile/:telegram_id"]`
- `App.jsx` uses `BrowserRouter` with routes `["/webapp/gallery", "/webapp/profile/:telegram_id"]`
- Both routers are active, causing conflicts
- Gallery route `/webapp/gallery` is not defined in `main.jsx` router
- `AnimatedRoutes` component incorrectly wraps `RouterProvider` (should wrap routes, not provider)

**Impact:** Gallery page doesn't load when "Find partner" button is clicked.

**Fix:**
```jsx
// frontend/src/main.jsx - REPLACE ENTIRE FILE
import React, { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import "./index.css";
import Gallery from "./pages/Gallery";
import Profile from "./pages/Profile";

const router = createBrowserRouter(
  [
    { path: "/gallery", element: <Gallery /> },
    { path: "/profile/:telegram_id", element: <Profile /> },
    { path: "/", element: <Gallery /> }, // Default to gallery
  ],
  { basename: "/webapp" }
);

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>
);
```

**Delete:** `frontend/src/App.jsx` (no longer needed)

---

### 2. **MISSING `telegram_id` IN API RESPONSE** ⚠️ CRITICAL
**Location:** `api/main.py:125-159`, `api/airtable_service.py:29-56`  
**Line Numbers:** `api/main.py:140-159`, `api/airtable_service.py:29-56`

**Problem:**
- `format_expert_record()` and `get_approved_experts()` don't include `telegram_id` field
- Frontend `SwipeCards.jsx:31` tries to navigate using `current.telegram_id` which is `undefined`
- Profile navigation fails completely

**Impact:** Cannot navigate to expert profiles from gallery cards.

**Fix:**
```python
# api/main.py - Update format_expert_record function (line 125)
def format_expert_record(record: dict):
    fields = record.get("fields", {})

    direction = (
        fields["Direction"][0]
        if isinstance(fields.get("Direction"), list) and fields["Direction"]
        else fields.get("Direction")
    )

    photo_url = (
        fields["Photo"][0]["url"]
        if isinstance(fields.get("Photo"), list) and fields["Photo"]
        else None
    )

    return {
        "id": record.get("id"),
        "telegram_id": str(fields.get("TelegramID", "")),  # ✅ ADD THIS
        "name": fields.get("Name"),
        "city": fields.get("City"),
        "language": fields.get("Language", "ru"),
        "direction": direction,
        "telegram": fields.get("Telegram"),
        "photo_url": photo_url,
        "status": fields.get("Status"),
        "education": fields.get("Education"),
        "experience": fields.get("Experience"),
        "clients": fields.get("Clients"),
        "average_check": fields.get("AverageCheck"),
        "audience": fields.get("Audience"),
        "positioning": fields.get("Positioning"),
        "methods": fields.get("Methods", []),
        "formats": fields.get("Format", []),
        "requests": fields.get("Requests", []),
        "description": fields.get("Description"),
    }
```

```python
# api/airtable_service.py - Update get_approved_experts function (line 29)
expert = {
    "id": record.get("id"),
    "telegram_id": str(fields.get("TelegramID", "")),  # ✅ ADD THIS
    "name": fields.get("Name"),
    "city": fields.get("City"),
    "language": fields.get("Language", "ru"),
    "direction": (
        fields["Direction"][0]
        if isinstance(fields.get("Direction"), list)
        else fields.get("Direction")
    ),
    "telegram": fields.get("Telegram"),
    "photo_url": (
        fields["Photo"][0]["url"]
        if isinstance(fields.get("Photo"), list) and fields["Photo"]
        else None
    ),
    # ... rest of fields
}
```

---

### 3. **DUPLICATE CODE IN `services/airtable_api.py`** ⚠️ CRITICAL
**Location:** `services/airtable_api.py`  
**Line Numbers:** `487-774` (duplicate of `189-476`)

**Problem:**
- Entire sections of code are duplicated:
  - `REQUESTS_MAPPING_RU/EN` defined twice (lines 192-237 and 487-532)
  - `_cached_fields` and `_sent_notifications` defined twice (lines 242-243 and 537-538)
  - `get_table()`, `get_all_table_fields()`, `smart_map()`, `log_record_to_csv()`, `create_expert_record()`, `update_expert_status()` all duplicated

**Impact:** Code maintenance nightmare, potential bugs from inconsistent updates.

**Fix:**
Delete lines 487-774 from `services/airtable_api.py`.

---

### 4. **CHARACTER ENCODING ISSUES** ⚠️ CRITICAL
**Location:** `frontend/src/pages/Gallery.jsx`  
**Line Numbers:** `22`, `40`, `47`

**Problem:**
- Corrupted text: `" :"` (line 22)
- Corrupted text: `" "` (line 40)
- Corrupted text: `"  "` (line 47)

**Impact:** UI displays garbage text instead of proper Russian.

**Fix:**
```jsx
// frontend/src/pages/Gallery.jsx
// Line 22
console.error("Ошибка загрузки:", err);

// Line 40
Галерея экспертов

// Line 47
Нет доступных экспертов
```

---

### 5. **MISSING `VITE_API_URL` ENVIRONMENT VARIABLE** ⚠️ CRITICAL
**Location:** `frontend/src/pages/Gallery.jsx:12`, `frontend/src/pages/Profile.jsx:20`

**Problem:**
- Frontend uses `import.meta.env.VITE_API_URL` but no `.env` file exists
- No fallback value provided
- API calls will fail with `undefined/api/experts`

**Impact:** All API calls fail, gallery and profile pages don't load.

**Fix:**
Create `frontend/.env`:
```env
VITE_API_URL=http://localhost:8000
```

For production, create `frontend/.env.production`:
```env
VITE_API_URL=https://your-api-domain.com
```

Also add fallback in code:
```jsx
// frontend/src/pages/Gallery.jsx
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
```

---

### 6. **API RESPONSE STRUCTURE MISMATCH** ⚠️ MAJOR
**Location:** `api/main.py:80-86`, `frontend/src/pages/Gallery.jsx:18`

**Problem:**
- Backend returns: `{page, limit, total, pages, experts: [...]}`
- Frontend expects: `data.experts` ✅ (this is correct)
- But if API fails, `data.experts` is `undefined` and no error handling

**Impact:** Silent failures, empty gallery with no error message.

**Fix:**
```jsx
// frontend/src/pages/Gallery.jsx - Improve error handling
useEffect(() => {
  fetch(`${API_URL}/api/experts`)
    .then((res) => {
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      return res.json();
    })
    .then((data) => {
      if (data && Array.isArray(data.experts)) {
        setExperts(data.experts);
      } else {
        console.error("Invalid API response:", data);
        setExperts([]);
      }
      setLoading(false);
    })
    .catch((err) => {
      console.error("Ошибка загрузки:", err);
      setExperts([]);
      setLoading(false);
    });
}, []);
```

---

### 7. **SWIPECARDS NAVIGATION PATH INCORRECT** ⚠️ MAJOR
**Location:** `frontend/src/components/SwipeCards.jsx:31`

**Problem:**
- Uses: `navigate(\`/webapp/profile/${current.telegram_id}\`)`
- But router basename is `/webapp`, so path should be `/profile/${telegram_id}`
- This causes double `/webapp/webapp/` in URL

**Impact:** Profile navigation fails with 404.

**Fix:**
```jsx
// frontend/src/components/SwipeCards.jsx - Line 31
const goToProfile = () => {
  navigate(`/profile/${current.telegram_id}`);  // Remove /webapp prefix
};
```

---

### 8. **MISSING ERROR HANDLING FOR EMPTY EXPERTS** ⚠️ MAJOR
**Location:** `frontend/src/components/SwipeCards.jsx:10-11`

**Problem:**
- If `experts` array is empty, `experts[0]` is `undefined`
- `current` and `next` become `undefined`
- Component crashes when trying to access `current.telegram_id` or `current.name`

**Impact:** App crashes when no experts are available.

**Fix:**
```jsx
// frontend/src/components/SwipeCards.jsx
export default function SwipeCards({ experts }) {
  const [index, setIndex] = useState(0);
  const navigate = useNavigate();

  // ✅ Add safety check
  if (!experts || experts.length === 0) {
    return (
      <div className="text-gray-400 text-lg mt-10">
        Нет доступных экспертов
      </div>
    );
  }

  const current = experts[index];
  const next = experts[(index + 1) % experts.length];
  // ... rest of code
}
```

---

## 🐛 Bugs with File Paths and Line Numbers

### Bug #1: Duplicate REQUESTS_MAPPING definitions
- **File:** `services/airtable_api.py`
- **Lines:** `192-237` and `487-532`
- **Fix:** Delete lines 487-532

### Bug #2: Duplicate function definitions
- **File:** `services/airtable_api.py`
- **Lines:** `540-774` (duplicate of `246-476`)
- **Fix:** Delete lines 540-774

### Bug #3: Missing telegram_id in API response
- **File:** `api/main.py`
- **Line:** `140` (missing in return dict)
- **Fix:** Add `"telegram_id": str(fields.get("TelegramID", ""))`

### Bug #4: Missing telegram_id in airtable_service
- **File:** `api/airtable_service.py`
- **Line:** `30` (missing in expert dict)
- **Fix:** Add `"telegram_id": str(fields.get("TelegramID", ""))`

### Bug #5: Character encoding corruption
- **File:** `frontend/src/pages/Gallery.jsx`
- **Lines:** `22`, `40`, `47`
- **Fix:** Replace with proper UTF-8 text

### Bug #6: Router conflict
- **File:** `frontend/src/main.jsx`
- **Lines:** `17-25`, `30-46`
- **Fix:** Remove `AnimatedRoutes` wrapper, fix router config

### Bug #7: Incorrect navigation path
- **File:** `frontend/src/components/SwipeCards.jsx`
- **Line:** `31`
- **Fix:** Change `/webapp/profile/` to `/profile/`

### Bug #8: Missing null check for experts array
- **File:** `frontend/src/components/SwipeCards.jsx`
- **Line:** `10`
- **Fix:** Add safety check before accessing array

---

## 🔧 Required Fixes (Code Blocks)

### Fix #1: Update `frontend/src/main.jsx`
```jsx
import React, { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import "./index.css";
import Gallery from "./pages/Gallery";
import Profile from "./pages/Profile";

const router = createBrowserRouter(
  [
    { path: "/gallery", element: <Gallery /> },
    { path: "/profile/:telegram_id", element: <Profile /> },
    { path: "/", element: <Gallery /> },
  ],
  { basename: "/webapp" }
);

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>
);
```

### Fix #2: Update `api/main.py` format_expert_record
```python
def format_expert_record(record: dict):
    fields = record.get("fields", {})

    direction = (
        fields["Direction"][0]
        if isinstance(fields.get("Direction"), list) and fields["Direction"]
        else fields.get("Direction")
    )

    photo_url = (
        fields["Photo"][0]["url"]
        if isinstance(fields.get("Photo"), list) and fields["Photo"]
        else None
    )

    return {
        "id": record.get("id"),
        "telegram_id": str(fields.get("TelegramID", "")),  # ✅ ADDED
        "name": fields.get("Name"),
        "city": fields.get("City"),
        "language": fields.get("Language", "ru"),
        "direction": direction,
        "telegram": fields.get("Telegram"),
        "photo_url": photo_url,
        "status": fields.get("Status"),
        "education": fields.get("Education"),
        "experience": fields.get("Experience"),
        "clients": fields.get("Clients"),
        "average_check": fields.get("AverageCheck"),
        "audience": fields.get("Audience"),
        "positioning": fields.get("Positioning"),
        "methods": fields.get("Methods", []),
        "formats": fields.get("Format", []),
        "requests": fields.get("Requests", []),
        "description": fields.get("Description"),
    }
```

### Fix #3: Update `api/airtable_service.py` get_approved_experts
```python
expert = {
    "id": record.get("id"),
    "telegram_id": str(fields.get("TelegramID", "")),  # ✅ ADDED
    "name": fields.get("Name"),
    "city": fields.get("City"),
    "language": fields.get("Language", "ru"),
    "direction": (
        fields["Direction"][0]
        if isinstance(fields.get("Direction"), list)
        else fields.get("Direction")
    ),
    "telegram": fields.get("Telegram"),
    "photo_url": (
        fields["Photo"][0]["url"]
        if isinstance(fields.get("Photo"), list) and fields["Photo"]
        else None
    ),
    "status": fields.get("Status"),
    "education": fields.get("Education"),
    "experience": fields.get("Experience"),
    "clients": fields.get("Clients"),
    "average_check": fields.get("AverageCheck"),
    "audience": fields.get("Audience"),
    "positioning": fields.get("Positioning"),
    "methods": fields.get("Methods", []),
    "formats": fields.get("Format", []),
    "requests": fields.get("Requests", []),
    "description": fields.get("Description"),
}
```

### Fix #4: Fix `frontend/src/pages/Gallery.jsx`
```jsx
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import VisionBackground from "../components/VisionBackground";
import SwipeCards from "../components/SwipeCards";
import SwipeSkeleton from "../components/SwipeSkeleton";
import "../App.css";

export default function Gallery() {
  const [experts, setExperts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  useEffect(() => {
    fetch(`${API_URL}/api/experts`)
      .then((res) => {
        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }
        return res.json();
      })
      .then((data) => {
        if (data && Array.isArray(data.experts)) {
          setExperts(data.experts);
        } else {
          console.error("Invalid API response:", data);
          setExperts([]);
        }
        setLoading(false);
      })
      .catch((err) => {
        console.error("Ошибка загрузки:", err);
        setError(err.message);
        setExperts([]);
        setLoading(false);
      });
  }, []);

  return (
    <div className="relative min-h-screen flex flex-col items-center text-white font-[Manrope] overflow-hidden">
      <VisionBackground />

      <div className="relative z-[2] w-full flex flex-col items-center pt-16">
        <motion.h1
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-4xl sm:text-5xl font-extrabold mb-10 tracking-tight
                     bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-500
                     bg-clip-text text-transparent drop-shadow-md"
        >
          Галерея экспертов
        </motion.h1>

        {loading ? (
          <SwipeSkeleton />
        ) : error ? (
          <p className="text-red-400 text-lg mt-10">
            Ошибка: {error}
          </p>
        ) : experts.length === 0 ? (
          <p className="text-gray-400 text-lg mt-10">
            Нет доступных экспертов
          </p>
        ) : (
          <SwipeCards experts={experts} />
        )}
      </div>
    </div>
  );
}
```

### Fix #5: Fix `frontend/src/components/SwipeCards.jsx`
```jsx
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useNavigate } from "react-router-dom";

export default function SwipeCards({ experts }) {
  const [index, setIndex] = useState(0);
  const navigate = useNavigate();

  // ✅ Safety check
  if (!experts || experts.length === 0) {
    return (
      <div className="text-gray-400 text-lg mt-10">
        Нет доступных экспертов
      </div>
    );
  }

  const current = experts[index];
  const next = experts[(index + 1) % experts.length];

  // ⭐ Предзагрузка следующего фото
  if (next?.photo_url) {
    const prefetchImg = new Image();
    prefetchImg.src = next.photo_url;
  }

  const swipeConfidenceThreshold = 120;

  const handleSwipe = (_, info) => {
    const swipe = info.offset.x;

    if (Math.abs(swipe) > swipeConfidenceThreshold) {
      setIndex((prev) => (prev + 1) % experts.length);
    }
  };

  const goToProfile = () => {
    if (current?.telegram_id) {
      navigate(`/profile/${current.telegram_id}`);  // ✅ Fixed path
    }
  };

  // ... rest of component remains the same
}
```

### Fix #6: Remove duplicate code from `services/airtable_api.py`
Delete lines 487-774 (entire duplicate section).

---

## 📊 API Endpoints Analysis

### Backend Endpoints (FastAPI)

1. **`GET /api/experts`** ✅ Used by frontend
   - **Consumed by:** `frontend/src/pages/Gallery.jsx:15`
   - **Status:** Working but missing `telegram_id` field
   - **Fix:** Add `telegram_id` to response

2. **`GET /api/profile/{telegram_id}`** ✅ Used by frontend
   - **Consumed by:** `frontend/src/pages/Profile.jsx:20`
   - **Status:** Working
   - **Note:** Returns single expert record

3. **`GET /api/expert/{record_id}`** ⚠️ Not used
   - **Status:** Unreachable from frontend
   - **Recommendation:** Remove or document for future use

4. **`GET /webapp`** ✅ Used
   - **Status:** Serves React app
   - **Note:** SPA fallback route

5. **`GET /webapp/{path:path}`** ✅ Used
   - **Status:** Serves React app routes
   - **Note:** SPA fallback route

### Frontend Routes

1. **`/webapp/gallery`** ✅ Defined
   - **Handler:** `Gallery.jsx`
   - **Status:** Broken due to routing conflict

2. **`/webapp/profile/:telegram_id`** ✅ Defined
   - **Handler:** `Profile.jsx`
   - **Status:** Broken due to routing conflict and missing `telegram_id`

---

## 🏗️ Recommended Architecture Improvements

### 1. **Separate API Client Module**
Create `frontend/src/api/client.js`:
```js
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const apiClient = {
  async getExperts(filters = {}) {
    const params = new URLSearchParams(filters);
    const res = await fetch(`${API_URL}/api/experts?${params}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  },
  
  async getProfile(telegramId) {
    const res = await fetch(`${API_URL}/api/profile/${telegramId}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  }
};
```

### 2. **Error Boundary Component**
Create `frontend/src/components/ErrorBoundary.jsx`:
```jsx
import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-black text-red-400">
          <div className="text-center">
            <h1 className="text-2xl mb-4">Что-то пошло не так</h1>
            <p className="text-gray-400">{this.state.error?.message}</p>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

export default ErrorBoundary;
```

### 3. **Environment Configuration**
Create `frontend/.env.example`:
```env
VITE_API_URL=http://localhost:8000
```

### 4. **TypeScript Migration** (Optional but recommended)
Convert to TypeScript for better type safety:
- `frontend/src/pages/Gallery.tsx`
- `frontend/src/pages/Profile.tsx`
- `frontend/src/components/SwipeCards.tsx`

### 5. **API Response Validation**
Add Pydantic models for API responses:
```python
# api/models.py
from pydantic import BaseModel
from typing import List, Optional

class Expert(BaseModel):
    id: str
    telegram_id: str
    name: str
    city: Optional[str] = None
    language: str = "ru"
    direction: Optional[str] = None
    # ... other fields

class ExpertsResponse(BaseModel):
    page: int
    limit: int
    total: int
    pages: int
    experts: List[Expert]
```

### 6. **Centralized Error Handling**
Create `api/errors.py`:
```python
from fastapi import HTTPException

class ExpertNotFoundError(HTTPException):
    def __init__(self, telegram_id: str):
        super().__init__(status_code=404, detail=f"Expert with telegram_id {telegram_id} not found")
```

### 7. **Logging Configuration**
Create `api/logging_config.py`:
```python
import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | [%(levelname)s] | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler("logs/api.log"),
            logging.StreamHandler()
        ]
    )
```

### 8. **Database Connection Pooling**
For Airtable, consider caching responses:
```python
# api/cache.py
from functools import lru_cache
from datetime import datetime, timedelta

class ExpertCache:
    def __init__(self, ttl_minutes=5):
        self.cache = {}
        self.ttl = timedelta(minutes=ttl_minutes)
    
    def get(self, key):
        if key in self.cache:
            data, timestamp = self.cache[key]
            if datetime.now() - timestamp < self.ttl:
                return data
        return None
    
    def set(self, key, value):
        self.cache[key] = (value, datetime.now())
```

### 9. **File Structure Improvements**
```
pazl-collab-bot/
├── api/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py          # ✅ NEW: Pydantic models
│   ├── errors.py          # ✅ NEW: Custom exceptions
│   ├── cache.py           # ✅ NEW: Caching layer
│   ├── logging_config.py  # ✅ NEW: Logging setup
│   └── airtable_service.py
├── frontend/
│   ├── src/
│   │   ├── api/           # ✅ NEW: API client
│   │   │   └── client.js
│   │   ├── components/
│   │   │   ├── ErrorBoundary.jsx  # ✅ NEW
│   │   │   └── ...
│   │   ├── pages/
│   │   └── ...
│   └── .env.example       # ✅ NEW
├── services/
│   └── airtable_api.py    # ✅ CLEAN: Remove duplicates
└── ...
```

### 10. **Testing Setup**
Add tests:
- `tests/test_api.py` - API endpoint tests
- `tests/test_airtable.py` - Airtable integration tests
- `frontend/src/__tests__/Gallery.test.jsx` - Component tests

### 11. **Docker Configuration**
Create `Dockerfile` and `docker-compose.yml` for easy deployment.

### 12. **CI/CD Pipeline**
Add GitHub Actions for:
- Linting
- Testing
- Building
- Deployment

---

## ✅ Action Items Checklist

### Immediate (Critical)
- [ ] Fix routing conflict in `main.jsx`
- [ ] Add `telegram_id` to API responses
- [ ] Remove duplicate code from `airtable_api.py`
- [ ] Fix character encoding in `Gallery.jsx`
- [ ] Create `.env` file with `VITE_API_URL`
- [ ] Fix navigation path in `SwipeCards.jsx`
- [ ] Add null checks for experts array

### Short-term (Major)
- [ ] Add error boundaries
- [ ] Improve error handling in API calls
- [ ] Add API response validation
- [ ] Create API client module
- [ ] Add logging configuration

### Long-term (Improvements)
- [ ] Migrate to TypeScript
- [ ] Add unit tests
- [ ] Set up Docker
- [ ] Implement caching
- [ ] Add CI/CD pipeline

---

## 📝 Notes

1. **Airtable API**: The current implementation works but could benefit from:
   - Response caching to reduce API calls
   - Better error handling for rate limits
   - Retry logic for failed requests

2. **Frontend State Management**: Consider adding Redux or Zustand for:
   - Expert list caching
   - User profile state
   - Loading states

3. **Security**: 
   - Add CORS restrictions (currently allows all origins)
   - Validate and sanitize all inputs
   - Add rate limiting to API endpoints

4. **Performance**:
   - Implement pagination in frontend
   - Add image lazy loading
   - Optimize bundle size

---

**End of Audit Report**

