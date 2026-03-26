# Parabank Playwright Framework

Enterprise-grade Playwright + Pytest + BDD + API + Hybrid automation framework.

## 🚀 Framework Highlights

- UI Automation (Playwright + POM)
- BDD Automation (`pytest-bdd`)
- API Automation (Playwright API Request Context)
- Hybrid Testing (UI + API validation)
- Parallel Execution (`pytest-xdist`)
- Retry Mechanism for flaky failures
- HTML Reports with failure screenshots
- Allure reporting support
- Marker- and suite-based execution
- GitHub Actions CI integration
- Dockerized execution support
- Java-framework-style runner strategy adapted to pytest

## 🏗️ Architecture Diagram

```text
┌─────────────────────────────────────────────────────────────────────┐
│                             Test Layer                             │
│  Direct Tests | BDD Tests | API Tests | Hybrid Tests | Runners     │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        Orchestration Layer                          │
│      Fixtures | FrameworkContext | Hybrid Services | Hooks         │
└─────────────────────────────────────────────────────────────────────┘
                                │
                ┌────────────────┴────────────────┐
                ▼                                 ▼
┌───────────────────────────────┐   ┌───────────────────────────────┐
│           UI Layer            │   │           API Layer           │
│ BasePage | Page Objects       │   │ ApiClient | Services | Models │
│ Waits | Element Utils         │   │ Request Handling | Assertions │
└───────────────────────────────┘   └───────────────────────────────┘
               └────────────────┬────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Core Framework Utilities                         │
│ Config | Driver | Validation | Reporting | Logging | Test Data     │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     Execution / Infrastructure                      │
│ Local | Docker | GitHub Actions | Remote-ready design              │
└─────────────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
ParabankPlaywrightFramework/
├── .github/
│   └── workflows/
│       └── ci.yml
├── docker/
│   └── entrypoint.sh
├── src/
│   ├── main/
│   │   └── python/
│   │       └── com/
│   │           └── parabank/
│   │               └── automation/
│   │                   ├── api/
│   │                   │   ├── client/
│   │                   │   ├── models/
│   │                   │   └── services/
│   │                   ├── assertions/
│   │                   ├── base/
│   │                   ├── config/
│   │                   ├── context/
│   │                   ├── driver/
│   │                   ├── exceptions/
│   │                   ├── hybrid/
│   │                   │   └── services/
│   │                   ├── pages/
│   │                   ├── reports/
│   │                   ├── utils/
│   │                   └── validation/
│   └── test/
│       ├── python/
│       │   ├── api/
│       │   ├── bdd/
│       │   │   └── ui/
│       │   ├── direct/
│       │   ├── hybrid/
│       │   │   └── ui_api/
│       │   ├── hooks/
│       │   ├── runners/
│       │   ├── stepdefinitions/
│       │   │   └── ui/
│       │   └── conftest.py
│       └── resources/
│           ├── config/
│           ├── features/
│           │   └── ui/
│           └── testdata/
│               ├── dev/
│               ├── qa/
│               └── stage/
├── test-output/
├── .dockerignore
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── pytest.ini
├── requirements.txt
└── README.md
```

## 🧪 Local Execution Commands

### 🔹 Smoke Suite
```bash
pytest --suite=smoke --env=qa --framework-browser=chrome --framework-headless=false
```

### 🔹 Regression Suite
```bash
pytest --suite=regression --env=qa --framework-browser=chrome --framework-headless=false
```

### 🔹 Sanity Suite
```bash
pytest --suite=sanity --env=qa --framework-browser=chrome --framework-headless=false
```

### 🔹 UI Suite
```bash
pytest --suite=ui --env=qa --framework-browser=chrome --framework-headless=false
```

### 🔹 API Suite
```bash
pytest --suite=api --env=qa --framework-browser=chrome --framework-headless=false
```

### 🔹 Hybrid Suite
```bash
pytest --suite=hybrid --env=qa --framework-browser=chrome --framework-headless=false
```

## 🏃 Java-Style Runner Commands

### Smoke Runner
```bash
python src/test/python/runners/smoke_runner.py --env=qa --framework-browser=chrome --framework-headless=false
```

### Regression Runner
```bash
python src/test/python/runners/regression_runner.py --env=qa --framework-browser=chrome --framework-headless=false
```

### Sanity Runner
```bash
python src/test/python/runners/sanity_runner.py --env=qa --framework-browser=chrome --framework-headless=false
```

### UI Runner
```bash
python src/test/python/runners/ui_runner.py --env=qa --framework-browser=chrome --framework-headless=false
```

### API Runner
```bash
python src/test/python/runners/api_runner.py --env=qa --framework-browser=chrome --framework-headless=false
```

### Hybrid Runner
```bash
python src/test/python/runners/hybrid_runner.py --env=qa --framework-browser=chrome --framework-headless=false
```

## 🏷️ Marker / Suite Taxonomy

### Suite Markers
- `smoke` = stable, business-critical validation
- `regression` = broad end-to-end functional validation
- `sanity` = framework health and setup verification

### Functional Markers
- `ui` = pure UI validation
- `api` = API-only validation
- `hybrid` = UI + API validation in same business flow
- `integration` = broader integration-level flows

### Control Markers
- `serial` = non-parallel-safe tests
- `manual` = excluded from automated runs unless explicitly included
- `quarantined` = unstable tests temporarily isolated from regular execution

## ⚙️ Configuration Strategy

Configuration is resolved through:

- framework-level properties
- environment-specific properties (qa, stage, dev)
- CLI overrides
- environment variables for sensitive values

### Resolution Order
1. CLI override
2. Environment-specific property file
3. Framework property file
4. Default constant from code

### Sensitive Values

These may be resolved through environment variables:

- `PARABANK_USERNAME`
- `PARABANK_PASSWORD`
- `BROWSERSTACK_USERNAME`
- `BROWSERSTACK_ACCESS_KEY`

## 🔁 How Hybrid Testing Works

The hybrid flow follows the same strategy as the Java framework.

### Current Hybrid Flow
1. Login through UI
2. Navigate to Accounts Overview
3. Extract UI account ids
4. Extract customer id from page source
5. Extract browser session cookies
6. Call API using the same authenticated session
7. Compare UI account ids and API account ids

### Main Components
- `FrameworkContext`
- `AccountsApiService`
- `HybridAccountsService`
- `CookieUtils`
- `CustomerUtils`

This is a real hybrid implementation, not a mocked or isolated API-only check.

## 📡 API Framework Layer

The API layer follows this structure:

`ApiClient` → low-level request handling
`Services` → business-facing API actions
`Models` → reusable API data objects where needed

### Current example

`AccountsApiService`

This keeps request plumbing out of test files.

## 🧱 Page Object Layer

The Page Object layer encapsulates page behavior and locators.

### Current examples

- `LoginPage`
- `HomePage`
- `AccountsOverviewPage`

Tests should use page methods instead of raw locators.

## 🚀 GitHub Actions CI

### Workflow Location
`.github/workflows/ci.yml`

### Triggers
- Push
- Pull Request
- Manual (workflow_dispatch)

### Manual Inputs
- suite
- environment
- browser

### Supported CI Artifacts
- HTML report
- Allure results
- traces
- screenshots

### Required GitHub Secrets
- `PARABANK_USERNAME`
- `PARABANK_PASSWORD`
- `BROWSERSTACK_USERNAME`
- `BROWSERSTACK_ACCESS_KEY`

### Manual Workflow Execution
1. Open GitHub repository
2. Go to Actions
3. Select the CI workflow
4. Click Run workflow
5. Choose:
   - suite
   - environment
   - browser

## 🐳 Docker Execution

### Docker Files
- `Dockerfile`
- `docker-compose.yml`
- `docker/entrypoint.sh`
- `.dockerignore`

### Build Docker Image
```bash
docker compose build --no-cache
```

### Run Default Smoke Suite
```bash
docker compose up --abort-on-container-exit
```

### Run Regression Suite
```bash
SUITE=regression docker compose up --abort-on-container-exit
```

### Run Hybrid Suite
```bash
SUITE=hybrid docker compose up --abort-on-container-exit
```

### Run with Firefox
```bash
SUITE=smoke BROWSER=firefox docker compose up --abort-on-container-exit
```

### Run with Additional Pytest Arguments
```bash
PYTEST_EXTRA_ARGS="-n 2" docker compose up --abort-on-container-exit
```

### Docker Cleanup
```bash
docker compose down
```

### Docker Notes
- artifacts are written to `test-output/`
- framework suite strategy remains same inside Docker
- Docker execution is ARM-safe and channel-safe

## 📊 Reports & Artifacts

- HTML Report: `test-output/reports/report.html`
- Allure Results: `test-output/allure-results/`
- Screenshots: `test-output/screenshots/` and `test-output/reports/images/`
- Traces: `test-output/traces/`
- Videos: `test-output/videos/`

## ✅ Startup Validation

The framework validates these at startup:

- environment selection
- browser selection
- execution mode
- URI correctness
- numeric configuration values
- endpoint reachability
- artifact directory readiness

This helps fail fast on bad configuration.

## 🧠 FrameworkContext

FrameworkContext is the shared state object used across a test flow, especially hybrid tests.

### Current hybrid state includes:
- `customer_id`
- `cookie_header`
- `ui_account_ids`
- `api_account_ids`

This keeps shared data structured and prevents raw plumbing inside tests.

## 🪵 Logging

The framework uses centralized logging for:

- startup lifecycle
- browser lifecycle
- page interactions
- API requests
- hybrid orchestration
- failure diagnostics

This improves debugging and report usefulness.

## 🔄 Parallel Execution

Parallel execution is supported using `pytest-xdist`.

### Example:
```bash
pytest -n 3 --suite=regression --env=qa --framework-browser=chrome --framework-headless=true
```

Tests marked `serial` should be excluded from parallel runs.

## 📌 Recommended Execution Order

### Local
1. Smoke
2. UI
3. API
4. Hybrid
5. Regression

### CI
1. Smoke on PR
2. Full regression manually or on broader validation need
3. Hybrid as targeted validation
4. Sanity after major setup changes

### Docker
1. Smoke
2. Regression
3. Hybrid
4. Parallelized execution if needed

## ⚠️ Notes

- Hybrid tests are more stateful than pure UI tests
- Use `serial` for tests that should not run in parallel
- Use `manual` for intentionally excluded cases
- Use `quarantined` for temporarily unstable tests
- CI and Docker use the same suite model as local execution
- Browser/channel logic is Docker- and ARM-safe

## 🛣️ Future Enhancement Candidates

- additional hybrid scenarios
- BrowserStack / remote execution validation end to end
- stronger README with screenshots or diagrams as images
- splitting oversized framework files if they grow further

## ⚡ Quick Start

### Install dependencies
```bash
pip install -r requirements.txt
python -m playwright install
```

### Run smoke
```bash
pytest --suite=smoke --env=qa --framework-browser=chrome --framework-headless=false
```

### Run hybrid
```bash
pytest --suite=hybrid --env=qa --framework-browser=chrome --framework-headless=false
```

### Run Docker smoke
```bash
docker compose build --no-cache
docker compose up --abort-on-container-exit
```

## 📘 Final Summary

This framework supports:

- UI automation
- BDD automation
- API automation
- Hybrid UI + API validation
- suite-based runner strategy
- parallel execution
- retry support
- HTML + Allure reporting
- GitHub Actions CI
- Docker execution

It is designed to be maintainable, scalable, and aligned with enterprise automation practices.
