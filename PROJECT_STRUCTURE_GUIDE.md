# Enterprise Folder Structure & Development Standards Guide

**Project:** `mak-ai-services`  
**Architecture Style:** Production-Grade Modular Monorepo (Layered Architecture)  
**Tech Stack:** Python 3.12 (FastAPI) Backend Services + React 18 (Vite + Tailwind CSS) Frontend  
**Database:** PostgreSQL 16 with `pgvector`  

---

## 1. Visual Repository Tree

```
mak-ai-services/                               <-- SINGLE GIT REPOSITORY ROOT
├── .env                                       <-- Single Source of Truth for Environment Variables
├── .env.example                               <-- Template for new team members
├── docker-compose.yml                         <-- Multi-container PostgreSQL (pgvector) + Redis
├── schema.sql                                 <-- Initial unified PostgreSQL DDL migrations
├── seed_data.sql                              <-- Seed data (colleges, test users, sample courses)
│
├── frontend/                                  <-- STUDENT 1 (React 18 + Vite + Tailwind CSS)
│   ├── public/                                (Favicons, public static files)
│   ├── src/
│   │   ├── assets/                            (Images, logos, custom svg icons)
│   │   ├── components/
│   │   │   ├── common/                        (Reusable UI buttons, modals, input fields, badges)
│   │   │   └── layout/                        (Navbar, Sidebar, Footer, ProtectedRoute wrappers)
│   │   ├── context/                           (Global React state: AuthContext, TenantContext)
│   │   ├── hooks/                             (Custom React hooks: useAuth, useDebounce, useQuota)
│   │   ├── pages/                             (Page views organized strictly by User Persona)
│   │   │   ├── auth/                          (Login, Register, ForgotPassword)
│   │   │   ├── student/                       (SyllabusChat, LearningHub, ProjectStudio, Portfolio)
│   │   │   ├── faculty/                       (BloomsGenerator, LessonPlans, ReviewProjects)
│   │   │   └── admin/                         (CollegeSettings, SeatUsage, NAACExport)
│   │   ├── services/                          (Axios API client and endpoint functions)
│   │   └── utils/                             (Date formatters, token decoders, constants)
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.js
│
├── services/                                  <-- STUDENT 2 & TECH LEAD (Backend Services)
│   ├── api_gateway/                           <-- Central Reverse Proxy & Rate Limiter (Port 8000)
│   │   ├── core/                              (config.py, auth_middleware.py, rate_limiter.py)
│   │   ├── routes/                            (proxy_routes.py, health_routes.py)
│   │   ├── main.py                            (FastAPI gateway entrypoint)
│   │   └── requirements.txt
│   │
│   ├── identity_service/                      <-- Authentication & Users (Port 8001)
│   │   ├── core/                              (config.py, database.py, security.py, dependencies.py)
│   │   ├── models/                            (user_model.py, role_model.py)
│   │   ├── schemas/                           (user_schema.py, token_schema.py)
│   │   ├── services/                          (auth_service.py, user_service.py)
│   │   ├── routes/                            (auth_router.py, user_router.py)
│   │   ├── main.py                            (FastAPI service entrypoint)
│   │   └── requirements.txt
│   │
│   ├── tenant_service/                        <-- Colleges & Seat Caps (Port 8002)
│   │   ├── core/                              (config.py, database.py)
│   │   ├── models/                            (tenant_model.py, module_model.py)
│   │   ├── schemas/                           (tenant_schema.py)
│   │   ├── services/                          (tenant_service.py, seat_validator.py)
│   │   ├── routes/                            (tenant_router.py)
│   │   ├── main.py
│   │   └── requirements.txt
│   │
│   ├── knowledge_rag_service/                 <-- Syllabus PDF & pgvector RAG (Port 8003)
│   │   ├── core/                              (config.py, database.py, vector_store.py)
│   │   ├── models/                            (document_model.py, chunk_model.py)
│   │   ├── schemas/                           (rag_schema.py, query_schema.py)
│   │   ├── services/                          (pdf_extractor.py, embedding_service.py, rag_engine.py)
│   │   ├── routes/                            (rag_router.py, upload_router.py)
│   │   ├── main.py
│   │   └── requirements.txt
│   │
│   ├── faculty_ai_service/                    <-- Bloom's Question Banks & Lessons (Port 8004)
│   │   ├── core/                              (config.py, database.py)
│   │   ├── models/                            (faculty_content_model.py)
│   │   ├── schemas/                           (blooms_schema.py, lesson_plan_schema.py)
│   │   ├── services/                          (blooms_generator.py, docx_exporter.py)
│   │   ├── routes/                            (faculty_router.py)
│   │   ├── main.py
│   │   └── requirements.txt
│   │
│   ├── project_studio_service/                <-- Project Milestones & Verification (Port 8005)
│   │   ├── core/                              (config.py, database.py)
│   │   ├── models/                            (project_model.py, milestone_model.py)
│   │   ├── schemas/                           (project_schema.py, milestone_schema.py)
│   │   ├── services/                          (project_service.py, idea_generator.py)
│   │   ├── routes/                            (project_router.py)
│   │   ├── main.py
│   │   └── requirements.txt
│   │
│   └── reporting_service/                     <-- NAAC Criteria 2.3 & Management Reports (Port 8006)
│       ├── core/                              (config.py, database.py)
│       ├── models/                            (audit_log_model.py)
│       ├── schemas/                           (report_schema.py)
│       ├── services/                          (naac_exporter.py, metrics_aggregator.py)
│       ├── routes/                            (reporting_router.py)
│       ├── main.py
│       └── requirements.txt
│
└── shared/                                    <-- Shared Utilities Across Services
    └── base_models.py                         (Common TimestampMixin, UUIDMixin)
```

---

## 2. Deep Dive: What Goes into Each Frontend Subfolder? (`frontend/`)

Assigned to: **Student Developer 1 (React 18 + Vite + Tailwind CSS)**

### `src/assets/`
* **What goes here:** Static media assets like the AMK logo, college partner banners, default user avatar SVGs.
* **Code Example:** `logo.svg`, `default-avatar.png`.

### `src/components/common/`
* **What goes here:** Reusable, stateless UI atoms and molecules used throughout the application.
* **Rules:** Must NEVER make direct API calls. They only receive `props` and emit callbacks (`onClick`, `onChange`).
* **Files:**
  * `Button.jsx` — Tailwind-styled button with loading spinner state (`isLoading`).
  * `Modal.jsx` — Reusable popup dialog with overlay backdrop and close button.
  * `Badge.jsx` — Color-coded tags (e.g. Bloom's Taxonomy badges: `L1: Remember` [Blue], `L3: Apply` [Green]).
  * `Input.jsx` — Form input field with validation error message display.

### `src/components/layout/`
* **What goes here:** Structural layout components that wrap around pages.
* **Files:**
  * `Navbar.jsx` — Top navigation bar with college name, user profile dropdown, and the **AI Quota Pill** (`⚡ 18/25 queries left`).
  * `Sidebar.jsx` — Collapsible sidebar displaying navigation links according to the user's role (`STUDENT`, `FACULTY`, `ADMIN`).
  * `ProtectedRoute.jsx` — React Router wrapper that checks if JWT exists and whether the user's role matches required permissions (redirects unauthorized users to `/login`).

### `src/context/`
* **What goes here:** Global React state providers using `React.createContext`.
* **Files:**
  * `AuthContext.jsx` — Stores `user`, `token`, `role`, and exposes `login(email, pass)` and `logout()` to any component.
  * `TenantContext.jsx` — Stores the currently active college branding, logo, and enabled module flags.

### `src/hooks/`
* **What goes here:** Custom React hooks that encapsulate complex logic so components remain clean and readable.
* **Files:**
  * `useAuth.js` — Quick shortcut hook: `const { user, role, logout } = useAuth();`
  * `useQuota.js` — Polls or updates remaining daily AI query count.
  * `useDebounce.js` — Debounces search inputs to avoid triggering API calls on every keystroke.

### `src/pages/` (Strictly Organized by Persona)
* **What goes here:** Full-screen views mapped to routes in `App.jsx`.
* **Subfolders:**
  * `pages/auth/Login.jsx` — Login form with college code, email, password.
  * `pages/student/SyllabusChat.jsx` — Full ChatGPT-style interface with real-time SSE token streaming and citation badges.
  * `pages/student/LearningHub.jsx` — Course card grid and markdown lesson viewer.
  * `pages/student/ProjectStudio.jsx` — Milestone submission Kanban board with GitHub commit link inputs.
  * `pages/faculty/BloomsGenerator.jsx` — Form with Subject, Unit, and Bloom's level checkboxes + interactive review editor.
  * `pages/admin/AdminDashboard.jsx` — Seat usage progress bars and one-click NAAC Criteria 2.3 export button.

### `src/services/`
* **What goes here:** All network communication. No React component should write raw `fetch()` or `axios.get()` calls.
* **Files:**
  * `api.js` — Central Axios instance configured with `baseURL` and an HTTP Request Interceptor that automatically attaches `Authorization: Bearer <token>`.
  * `authApi.js` — `loginApi(data)`, `registerApi(data)`.
  * `ragApi.js` — `askSyllabusApi(query)`, `uploadPdfApi(formData)`.
  * `facultyApi.js` — `generateQuestionsApi(params)`, `approveContentApi(id)`.

---

## 3. Deep Dive: What Goes into Each Backend Service Subfolder?

Assigned to: **Student Developer 2 & Technical Lead (Python 3.12 + FastAPI)**

Every single service under `services/<service_name>/` follows the exact same **Layered Clean Architecture**:

```
 [HTTP Request]
        │
        ▼
   [routes/]       <-- Layer 1: Validates incoming request using schemas, returns HTTP status codes
        │
        ▼
  [services/]      <-- Layer 2: Core business logic, AI calls, validations, calculations
        │
        ▼
   [models/]       <-- Layer 3: SQLAlchemy ORM models representing PostgreSQL tables
        │
        ▼
   [Database]
```

### `core/` (Service Foundation)
* **What goes here:** System configuration, database connections, and FastAPI request dependencies.
* **Files:**
  * `config.py` — Reads the root `.env` using `pydantic-settings`.
    ```python
    from pydantic_settings import BaseSettings, SettingsConfigDict
    from pathlib import Path

    ROOT_ENV = Path(__file__).resolve().parents[4] / ".env"

    class Settings(BaseSettings):
        DB_HOST: str = "localhost"
        DB_PORT: int = 5432
        DB_NAME: str = "amk_college_platform"
        DB_USER: str = "postgres"
        DB_PASSWORD: str = "rootpassword123"
        JWT_SECRET: str
        GEMINI_API_KEY: str = ""

        model_config = SettingsConfigDict(env_file=ROOT_ENV, extra="ignore")

    settings = Settings()
    ```
  * `database.py` — Configures the async SQLAlchemy engine and session dependency:
    ```python
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
    from app.core.config import settings

    DATABASE_URL = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

    engine = create_async_engine(DATABASE_URL, echo=False)
    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

    async def get_db():
        async with AsyncSessionLocal() as session:
            yield session
    ```
  * `security.py` — Password hashing utilities (`passlib[bcrypt]`) and JWT encoding/decoding (`python-jose`).
  * `dependencies.py` — Common FastAPI dependencies: `get_current_user`, `require_role(["FACULTY", "HOD"])`.

### `models/` (Database Layer)
* **What goes here:** SQLAlchemy declarative database models representing PostgreSQL tables.
* **Rules:**
  * Models define table columns, primary keys, foreign keys, and indexes.
  * Must inherit from `Base = declarative_base()`.
* **Example (`models/user_model.py`):**
  ```python
  from sqlalchemy import Column, String, Boolean, DateTime, func
  from sqlalchemy.dialects.postgresql import UUID
  import uuid
  from app.core.database import Base

  class User(Base):
      __tablename__ = "users"

      id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
      tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
      email = Column(String(255), nullable=False)
      password_hash = Column(String(255), nullable=False)
      full_name = Column(String(150), nullable=False)
      role = Column(String(50), nullable=False, default="STUDENT")
      is_active = Column(Boolean, default=True)
      created_at = Column(DateTime(timezone=True), server_default=func.now())
  ```

### `schemas/` (Data Transfer Objects & Validation Layer)
* **What goes here:** Pydantic v2 schemas that define the shape of incoming requests and outgoing responses.
* **Rules:**
  * Never expose internal database fields (like `password_hash`) in schemas.
  * Always enable `model_config = ConfigDict(from_attributes=True)` on response schemas so SQLAlchemy models serialize automatically.
* **Example (`schemas/user_schema.py`):**
  ```python
  from pydantic import BaseModel, EmailStr, Field, ConfigDict
  from uuid import UUID
  from typing import Optional

  # Incoming payload for registration
  class UserCreate(BaseModel):
      email: EmailStr
      password: str = Field(min_length=8)
      full_name: str
      department: str
      role: str = "STUDENT"

  # Outgoing response (safe for client, no password_hash)
  class UserResponse(BaseModel):
      id: UUID
      tenant_id: UUID
      email: EmailStr
      full_name: str
      role: str
      is_active: bool

      model_config = ConfigDict(from_attributes=True)
  ```

### `services/` (Business Logic Layer)
* **What goes here:** The brain of the service. Contains calculations, external API calls (Gemini/OpenAI), PDF extraction, and database persistence.
* **Rules:**
  * Route functions should be small and clean (10–15 lines). All heavy lifting lives inside `services/`.
* **Example (`services/auth_service.py`):**
  ```python
  from sqlalchemy.ext.asyncio import AsyncSession
  from sqlalchemy import select
  from app.models.user_model import User
  from app.schemas.user_schema import UserCreate
  from app.core.security import hash_password, verify_password

  class AuthService:
      @staticmethod
      async def register_user(db: AsyncSession, payload: UserCreate, tenant_id: str) -> User:
          hashed_pwd = hash_password(payload.password)
          user = User(
              tenant_id=tenant_id,
              email=payload.email,
              password_hash=hashed_pwd,
              full_name=payload.full_name,
              role=payload.role
          )
          db.add(user)
          await db.commit()
          await db.refresh(user)
          return user
  ```

### `routes/` (API Controller Layer)
* **What goes here:** FastAPI `APIRouter` instances that define URL endpoints, HTTP methods (`GET`, `POST`), request validation, and status codes.
* **Rules:**
  * Receives Pydantic schemas, calls the service, and returns the response schema.
* **Example (`routes/auth_router.py`):**
  ```python
  from fastapi import APIRouter, Depends, status
  from sqlalchemy.ext.asyncio import AsyncSession
  from app.schemas.user_schema import UserCreate, UserResponse
  from app.services.auth_service import AuthService
  from app.core.database import get_db

  router = APIRouter(prefix="/auth", tags=["Auth"])

  @router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
  async def register_student(payload: UserCreate, db: AsyncSession = Depends(get_db)):
      tenant_id = "c1f7a40b-7871-46c6-9964-16ce34927b23" # extracted from context
      new_user = await AuthService.register_user(db, payload, tenant_id)
      return new_user
  ```

### `main.py` (Service Entrypoint)
* **What goes here:** Initializes the FastAPI app, registers all routers, sets up CORS, and defines health checks.
* **Example (`main.py`):**
  ```python
  from fastapi import FastAPI
  from app.routes.auth_router import router as auth_router

  app = FastAPI(title="AMK Identity Service", version="1.0.0", docs_url="/docs")

  app.include_router(auth_router, prefix="/api/v1")

  @app.get("/health")
  async def health():
      return {"status": "healthy"}
  ```

---

## 4. Golden Rules for Developers & Students

1. **The Separation of Concerns Rule:**
   * Never write SQL queries or call Gemini API directly inside a `routes/` file. Always delegate to `services/`.
   * Never return a raw SQLAlchemy Model directly from a route. Always map to a Pydantic `response_model`.
2. **The 30-Minute Blocker Rule:**
   * If a student gets stuck on an import or database error for more than 30 minutes, they must post in the team chat immediately with the stack trace.
3. **Naming Conventions:**
   * **Python:** `snake_case` for filenames, variables, and functions (`auth_service.py`, `generate_blooms()`).
   * **Classes:** `PascalCase` (`AuthService`, `UserResponse`).
   * **React/JavaScript:** `PascalCase` for React components (`SyllabusChat.jsx`), `camelCase` for variables and hooks (`useAuth`, `handleClick`).

