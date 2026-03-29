# Parabank Playwright Framework

Enterprise-grade Playwright + Pytest + BDD + API + Hybrid automation framework for ParaBank.

This framework is designed to mirror strong Java enterprise automation practices while using Python, Playwright, pytest, and pytest-bdd.

---

## Framework highlights

- UI automation using Playwright and Page Object Model
- BDD automation using `pytest-bdd`
- API automation using Playwright API request context
- Hybrid UI + API validation flows
- Environment-aware configuration
- Centralized assertions, logging, waits, and reporting
- Retry support for transient failures
- Parallel execution support with `pytest-xdist`
- HTML reporting, Allure results, screenshots, traces, and videos
- Suite-based execution strategy
- GitHub Actions CI integration
- Dockerized execution support

---

## Tech stack

- Python 3.11+
- Playwright
- Pytest
- pytest-bdd
- pytest-html
- Allure
- pytest-rerunfailures
- pytest-xdist
- Faker
- Flake8
- Pylint
- Black
- isort

---

## Project structure

```text
ParabankPlaywrightFramework/
├── .github/
│   └── workflows/
│       └── ci.yml
├── config/
│   ├── flake8
│   └── pylint
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
│   │                   │   ├── endpoints/
│   │                   │   ├── models/
│   │                   │   └── services/
│   │                   ├── assertions/
│   │                   ├── base/
│   │                   ├── config/
│   │                   ├── context/
│   │                   ├── dataproviders/
│   │                   ├── driver/
│   │                   ├── exceptions/
│   │                   ├── hybrid/
│   │                   │   └── services/
│   │                   ├── models/
│   │                   ├── pages/
│   │                   ├── reports/
│   │                   ├── utils/
│   │                   └── validation/
│   └── test/
│       ├── python/
│       │   ├── api/
│       │   ├── bdd/
│       │   │   ├── api/
│       │   │   ├── hybrid/
│       │   │   └── ui/
│       │   ├── hooks/
│       │   ├── hybrid/
│       │   │   └── ui_api/
│       │   ├── runners/
│       │   ├── stepdefinitions/
│       │   │   ├── api/
│       │   │   ├── hybrid/
│       │   │   └── ui/
│       │   └── conftest.py
│       └── resources/
│           ├── config/
│           ├── features/
│           │   ├── api/
│           │   ├── hybrid/
│           │   └── ui/
│           └── testdata/
│               ├── dev/
│               ├── qa/
│               └── stage/
├── test-output/
├── .dockerignore
├── .env.example
├── .gitignore
├── conftest.py
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── pytest.ini
├── requirements.txt
└── README.md
```

## Framework architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                             Test Layer                             │
│     UI BDD | API BDD | Hybrid BDD | Direct API | Runners          │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        Orchestration Layer                          │
│   Pytest fixtures | Hooks | FrameworkContext | ScenarioContext     │
└─────────────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┴────────────────┐
                ▼                                ▼
┌───────────────────────────────┐   ┌───────────────────────────────┐
│            UI Layer           │   │           API Layer           │
│ BasePage | Pages | Waits      │   │ ApiClient | Services | Models │
│ ElementUtils | UiAssertions   │   │ ApiAssertions | Endpoints     │
└───────────────────────────────┘   └───────────────────────────────┘
                └───────────────┬────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     Core Framework Utilities                        │
│ Config | Validation | Logging | Reporting | Test Data | Drivers    │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   Execution / Infrastructure Layer                  │
│       Local | Parallel | Docker | GitHub Actions | Pages Site      │
└─────────────────────────────────────────────────────────────────────┘
```

## Setup instructions

### 1. Clone the project

```bash
git clone <your-repository-url>
cd ParabankPlaywrightFramework
```

### 2. Create and activate virtual environment

**macOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows PowerShell**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Playwright browsers

```bash
python -m playwright install
```

If system dependencies are needed in CI or Linux containers:

```bash
python -m playwright install --with-deps
```

### 5. Verify basic setup

```bash
pytest --env=qa --suite=smoke
```

## Environment configuration

The framework supports these environments:

- `qa`
- `stage`
- `dev`

Configuration is read from:

- `src/test/resources/config/framework.properties`
- `src/test/resources/config/qa.properties`
- `src/test/resources/config/stage.properties`
- `src/test/resources/config/dev.properties`

### Configuration resolution order

1. CLI arguments
2. Environment-specific property file
3. Framework property file
4. Code defaults

### Sensitive values

Sensitive values should come from environment variables.

#### Supported environment variables

- `PARABANK_USERNAME`
- `PARABANK_PASSWORD`
- `BROWSERSTACK_USERNAME`
- `BROWSERSTACK_ACCESS_KEY`

#### Example .env approach

Use `.env.example` as reference and create your own `.env` if needed.

## Supported suite values

The framework supports these `--suite` values:

- `all`
- `smoke`
- `regression`
- `sanity`
- `ui`
- `api`
- `hybrid`

**Important note**

`full` is not a valid suite value in this framework.

Use this instead:

```bash
pytest --env=qa --suite=all
```

## Local execution commands

### Run everything

```bash
pytest --env=qa --suite=all
```

### Smoke suite

```bash
pytest --env=qa --suite=smoke
```

### Regression suite

```bash
pytest --env=qa --suite=regression
```

### Sanity suite

```bash
pytest --env=qa --suite=sanity
```

### UI suite

```bash
pytest --env=qa --suite=ui
```

### API suite

```bash
pytest --env=qa --suite=api
```

### Hybrid suite

```bash
pytest --env=qa --suite=hybrid
```

## Common CLI overrides

### Run on a specific browser

```bash
pytest --env=qa --suite=ui --framework-browser=chrome
pytest --env=qa --suite=ui --framework-browser=firefox
pytest --env=qa --suite=ui --framework-browser=edge
```

### Run headless

```bash
pytest --env=qa --suite=ui --framework-browser=chrome --framework-headless=true
```

### Run headed locally

```bash
pytest --env=qa --suite=ui --framework-browser=chrome --framework-headless=false
```

### Override base URL

```bash
pytest --env=qa --suite=ui --framework-base-url=https://parabank.parasoft.com/parabank
```

### Override API base URL

```bash
pytest --env=qa --suite=api --api-base-url=https://parabank.parasoft.com/parabank/services_proxy/bank
```

### Override username/password

```bash
pytest --env=qa --suite=ui --username=john --password=demo
```

## Java-style runner commands

These runner files mirror Java-framework-style suite execution.

### Smoke runner

```bash
python src/test/python/runners/smoke_runner.py --env=qa --framework-browser=chrome --framework-headless=false
```

### Regression runner

```bash
python src/test/python/runners/regression_runner.py --env=qa --framework-browser=chrome --framework-headless=false
```

### Sanity runner

```bash
python src/test/python/runners/sanity_runner.py --env=qa --framework-browser=chrome --framework-headless=false
```

### UI runner

```bash
python src/test/python/runners/ui_runner.py --env=qa --framework-browser=chrome --framework-headless=false
```

### API runner

```bash
python src/test/python/runners/api_runner.py --env=qa --framework-browser=chrome --framework-headless=false
```

### Hybrid runner

```bash
python src/test/python/runners/hybrid_runner.py --env=qa --framework-browser=chrome --framework-headless=false
```

## BDD feature execution

### Run all UI BDD tests

```bash
pytest src/test/python/bdd/ui --env=qa -v
```

### Run all API BDD tests

```bash
pytest src/test/python/bdd/api --env=qa -v
```

### Run all Hybrid BDD tests

```bash
pytest src/test/python/bdd/hybrid --env=qa -v
```

### Run a single feature-backed BDD file

```bash
pytest src/test/python/bdd/ui/test_bdd_login.py --env=qa -v
pytest src/test/python/bdd/ui/test_bdd_transfer_funds.py --env=qa -v
```

## Marker strategy

### Suite markers

- `smoke`
- `regression`
- `sanity`

### Functional markers

- `ui`
- `api`
- `hybrid`
- `apiui`
- `integration`

### Control markers

- `serial`
- `manual`
- `quarantined`
- `slow`

### Domain markers

- `login`
- `negative`
- `positive`
- `billpay`
- `findtransactions`
- `accounts`
- `transferfunds`
- `opennewaccount`
- `api_authenticated`

### Marker examples

Run smoke only:

```bash
pytest -m smoke --env=qa
```

Run UI but exclude serial:

```bash
pytest -m "ui and not serial" --env=qa
```

Run transfer-funds tests:

```bash
pytest -m transferfunds --env=qa
```

## Parallel execution

Parallel execution is supported through pytest-xdist.

### Example

```bash
pytest -n 3 --dist=loadfile --env=qa --suite=regression
```

### Notes

- tests marked `serial` should not be run in parallel unless intentionally allowed
- screenshots, traces, and reports use parallel-safe naming
- framework supports thread-count style configuration through CLI/config

## Retry behavior

Retry support is available through pytest-rerunfailures and framework-level retry config.

### Example

```bash
pytest --env=qa --suite=ui --retry-count=1 --retry-delay=1
```

### Notes

- retries are useful for transient UI timing issues
- repeated business-state tests should still be made stable rather than relying on retries

## API framework usage

The API layer is structured as:

- `api/client` → low-level request handling
- `api/endpoints` → API route constants
- `api/models` → reusable response/domain models
- `api/services` → business-facing API operations

### Current examples

- `AccountsApiService`
- `CustomersApiService`

This keeps test code clean and avoids raw request plumbing inside step definitions.

## Hybrid framework usage

Hybrid testing combines UI and API state within the same business flow.

### Typical hybrid flow

1. Login in UI
2. Navigate in UI and capture business state
3. Extract customer/session information
4. Call API using same logical flow/session strategy
5. Compare UI and API data

### Current hybrid coverage

- account validation across UI and API
- account creation through UI with API-side verification

## Reporting and artifact locations

- **HTML report**: `test-output/reports/report.html`
- **Allure results**: `test-output/allure-results/`
- **Screenshots**: `test-output/screenshots/`, `test-output/reports/images/`
- **Traces**: `test-output/traces/`
- **Videos**: `test-output/videos/`

## Allure usage

### Generate Allure report locally

If you have Allure installed:

```bash
allure serve test-output/allure-results
```

Or:

```bash
allure generate test-output/allure-results --clean -o allure-report
allure open allure-report
```

## GitHub Actions CI

**Workflow file**: `.github/workflows/ci.yml`

### CI supports

- dependency installation
- Playwright browser setup
- quality gate
- suite-based execution
- browser matrix execution
- headless execution
- artifact upload
- GitHub Pages report publishing

### Workflow inputs

- suite
- environment
- browser mode
- browser selection
- execution mode
- workers

### Required GitHub secrets

- `PARABANK_USERNAME`
- `PARABANK_PASSWORD`
- `BROWSERSTACK_USERNAME`
- `BROWSERSTACK_ACCESS_KEY`

## Docker usage

### Build image

```bash
docker compose build --no-cache
```

### Run default flow

```bash
docker compose up --abort-on-container-exit
```

### Run smoke

```bash
SUITE=smoke docker compose up --abort-on-container-exit
```

### Run regression

```bash
SUITE=regression docker compose up --abort-on-container-exit
```

### Run hybrid

```bash
SUITE=hybrid docker compose up --abort-on-container-exit
```

### Run with specific browser

```bash
SUITE=smoke BROWSER=firefox docker compose up --abort-on-container-exit
```

### Pass extra pytest args

```bash
PYTEST_EXTRA_ARGS="-n 2 --dist=loadfile" docker compose up --abort-on-container-exit
```

### Cleanup

```bash
docker compose down
```

## Code quality commands

### Install dependencies

```bash
pip install -r requirements.txt
```

### Auto-format

```bash
black .
isort .
```

### Validation checks

```bash
black --check .
isort --check-only .
flake8 --config=config/flake8 .
pylint --rcfile=config/pylint src/main/python/com/parabank/automation src/test/python
```

### Recommended full sequence

```bash
black . && isort . && black --check . && isort --check-only . && flake8 --config=config/flake8 . && pylint --rcfile=config/pylint src/main/python/com/parabank/automation src/test/python
```

## Startup validation

The framework performs startup validation for items like:

- environment selection
- browser selection
- execution mode
- numeric config values
- URL validity
- artifact directory readiness
- runtime setup health

This helps fail fast on configuration issues.

## Onboarding guide for a new user

### Step 1

Clone the repo and create a virtual environment.

### Step 2

Install dependencies.

### Step 3

Install Playwright browsers.

### Step 4

Set required environment variables or local .env.

### Step 5

Run smoke suite:

```bash
pytest --env=qa --suite=smoke
```

### Step 6

Open generated HTML report:

```
test-output/reports/report.html
```

### Step 7

Run targeted suites as needed:

- UI
- API
- Hybrid
- Regression

## Recommended execution order

### Local developer workflow

1. Smoke
2. UI targeted flow
3. API targeted flow
4. Hybrid targeted flow
5. Regression

### CI workflow

1. Quality gate
2. Smoke on PR / quick validation
3. Broader suite execution on demand
4. Artifact and report publishing

## Troubleshooting

### 1. Invalid suite value

If you run:

```bash
pytest --env=qa --suite=full
```

You will get an invalid choice error.

Use:

```bash
pytest --env=qa --suite=all
```

### 2. Playwright browsers not installed

Install them:

```bash
python -m playwright install
```

### 3. Import/root path issues

Run from project root:

```bash
pytest --env=qa --suite=smoke
```

Do not run from nested directories unless you know the path implications.

### 4. Browser launches but tests fail immediately

Check:

- environment properties
- credentials
- base URL
- startup validation logs

### 5. HTML report not opening

Verify this file exists:

```
test-output/reports/report.html
```

### 6. Allure report not visible

Make sure `test-output/allure-results/` has content, then generate locally with Allure CLI.

### 7. Parallel failures

If stateful tests are involved:

- run them serially
- use `serial` marker
- avoid running business-state-sensitive flows in parallel

### 8. Retry confusion

Retries help with transient timing issues, but business-state failures should be fixed in test logic, not hidden by retries.

### 9. Quality check failures

Use:

```bash
black .
isort .
flake8 --config=config/flake8 .
pylint --rcfile=config/pylint src/main/python/com/parabank/automation src/test/python
```

Fix issues in code instead of weakening the rule set unless there is a strong framework reason.

## Notes and conventions

- Use page objects instead of raw locators in step files
- Use centralized assertions instead of scattered raw assertions
- Keep data in JSON providers
- Prefer suite-based execution over ad hoc command sprawl
- Keep hybrid flows intentional and business-driven
- Keep retries low and test design stable

## Final summary

This framework supports:

- UI automation
- API automation
- Hybrid UI + API validation
- BDD execution
- suite-based runners
- retry strategy
- parallel execution
- HTML and Allure reporting
- GitHub Actions CI
- Docker execution
- code quality tooling

It is designed to be maintainable, scalable, and aligned with enterprise automation practices.
