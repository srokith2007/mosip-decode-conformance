# Automated Conformance Testing for Inji Certify and Inji Verify

Automated harness for testing **Inji Certify** and **Inji Verify** against the **OpenID Foundation Conformance Suite**.

The project automates OpenID conformance test execution through REST APIs, integrates the results with the MOSIP `api-testrig`, supports combined execution, applies a regression benchmark, and runs in CI/CD.

---

## 1. Problem

Conformance testing currently involves multiple services and manual steps:

* Starting Inji Certify / Inji Verify and dependencies.
* Configuring OpenID test plans.
* Starting and monitoring tests.
* Collecting results.
* Integrating results with the MOSIP test framework.

This project automates the complete workflow to make testing **repeatable, programmatic, and CI/CD-ready**.

---

## 2. Solution

```text
                 Docker Compose
                      │
       ┌──────────────┼──────────────┐
       ▼              ▼              ▼
   Inji Certify   Inji Verify   OpenID Suite
       │              │              │
       └──────────────┼──────────────┘
                      ▼
             Python Conformance
                  Harness
                      │
                      ▼
               OpenID REST API
                      │
           Create → Start → Poll → Results
                      │
                      ▼
                Benchmark Gate
                      │
                      ▼
              MOSIP api-testrig
                      │
                      ▼
                    TestNG
```

### Key Implementation

| Requirement             | Implementation                                 |
| ----------------------- | ---------------------------------------------- |
| Dockerized environment  | `docker-compose.yml`                           |
| Certify conformance     | `configs/certify.json`                         |
| Verify conformance      | `configs/verify.json`                          |
| OpenID REST automation  | `conformance-harness/runner/`                  |
| Result processing       | `runner/results.py`                            |
| Regression benchmark    | `reports/benchmark.json`                       |
| api-testrig integration | `OpenIDConformanceTest.java`                   |
| Combined execution      | `run-full-stack-conformance.sh`                |
| CI/CD                   | `.github/workflows/full-stack-conformance.yml` |

---

## 3. Architecture

All services run on the Docker network:

```text
openid-conformance-net
```

### Main Services

| Service               | Purpose                  |
| --------------------- | ------------------------ |
| `certify`             | Inji Certify             |
| `certify-nginx`       | Certify proxy            |
| `database`            | Certify PostgreSQL       |
| `verify-service`      | Inji Verify              |
| `verify-postgres`     | Verify PostgreSQL        |
| `server`              | OpenID Conformance Suite |
| `conformance-nginx`   | Suite HTTPS endpoint     |
| `conformance-mongodb` | Suite MongoDB            |

---

## 4. Prerequisites

* Docker Desktop + Docker Compose
* Java 21
* Maven 3.9.6+
* Python 3.x
* Git
* Git Bash on Windows

Verify the environment:

```bash
java -version
mvn -version
python --version
docker --version
docker compose version
```

---

## 5. Installation

Clone the repository:

```bash
git clone https://github.com/srokith2007/mosip-decode-conformance.git
cd mosip-decode-conformance
```

Set up the Python harness:

```bash
cd conformance-harness
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
cd ..
```

---

## 6. Configuration

Configurations are stored in:

```text
conformance-harness/
└── configs/
    ├── certify.json
    └── verify.json
```

### Certify

```text
Plan:
oid4vci-1_0-issuer-haip-test-plan

Test:
oid4vci-1_0-issuer-metadata-test
```

### Verify

```text
Plan:
oid4vp-id3-verifier-test-plan

Test:
oid4vp-id3-verifier-happy-flow
```

Plan variants and component-specific settings are defined in the JSON configuration files.

---

## 7. Running

### Certify

```bash
./run-full-stack-conformance.sh --component certify
```

### Verify

```bash
./run-full-stack-conformance.sh --component verify
```

### Combined

```bash
./run-full-stack-conformance.sh --combined
```

The combined command executes both components through the MOSIP `api-testrig`.

---

## 8. OpenID REST Automation

The Python harness replaces manual Conformance Suite execution with an automated REST lifecycle:

```text
Create Plan
    ↓
Create Test
    ↓
Start Test
    ↓
Poll Status
    ↓
Process Results
    ↓
Benchmark Check
```
### REST API Operations

The harness communicates with the OpenID Conformance Suite using the following REST API operations:

| Method | Endpoint                             | Purpose                             |
| ------ | ------------------------------------ | ----------------------------------- |
| `GET`  | `/api/plan?length=1`                 | Check Conformance Suite readiness   |
| `POST` | `/api/plan`                          | Create/configure a test plan        |
| `POST` | `/api/runner`                        | Create a test execution from a plan |
| `POST` | `/api/runner/{module_id}`            | Start the test execution            |
| `GET`  | `/api/runner/{module_id}/wait-state` | Poll execution status               |

The harness handles the API calls programmatically and processes the resulting execution state and test results.

Implementation:

```text
conformance-harness/
├── runner/
│   ├── client.py
│   ├── test_plan.py
│   ├── executor.py
│   └── results.py
└── main.py
```

* `client.py` — HTTP communication with the Suite.
* `test_plan.py` — plan and test creation.
* `executor.py` — execution and polling.
* `results.py` — result normalization and benchmark checking.
* `main.py` — component execution entry point.

---

## 9. MOSIP api-testrig Integration

OpenID conformance execution is integrated into the MOSIP TestNG framework through:

```text
mosip-functional-tests/
└── apitest-commons/
    └── src/test/java/
        └── io/mosip/testrig/apirig/testrunner/
            └── OpenIDConformanceTest.java
```

### Execution Flow

```text
TestNG
  ↓
OpenIDConformanceTest
  ↓
Python Harness
  ↓
OpenID Conformance Suite
  ↓
Result
  ↓
TestNG
```

Run directly:

```bash
cd mosip-functional-tests/apitest-commons
mvn -Dtest=OpenIDConformanceTest test
```

---

## 10. Benchmark Gate

The project maintains a regression baseline:

```text
conformance-harness/reports/benchmark.json
```

The gate detects:

* Decrease in passed tests.
* Increase in failed tests.
* Increase in warnings.

Example:

```text
Baseline: 34 passed, 3 failed, 3 warnings

Current:  33 passed, 4 failed, 4 warnings

→ BENCHMARK: FAIL
```

The benchmark is a **project-level regression check**, not an official OpenID certification score.

A benchmark pass does not mean that the OpenID Conformance Suite itself reported complete conformance.

---

## 11. CI/CD

GitHub Actions workflow:

```text
.github/workflows/full-stack-conformance.yml
```

The workflow:

1. Checks out the repository.
2. Installs Java and Python.
3. Installs Python dependencies.
4. Configures the Suite hostname.
5. Runs the combined conformance workflow.
6. Stops Docker services.

### Supported Triggers

* Push to `master` / `main`
* Published release
* Manual execution

---

## 12. Testing

The implementation was tested for:

| Test Case                   | Result |
| --------------------------- | ------ |
| Certify plan execution      | PASS   |
| Verify plan execution       | PASS   |
| Invalid endpoint            | PASS   |
| Conformance failure capture | PASS   |
| Benchmark regression        | PASS   |
| Combined execution          | PASS   |
| Service unavailable         | PASS   |
| Network failure             | PASS   |
| Invalid configuration       | PASS   |
| Service startup/recovery    | PASS   |
| OpenID test failure         | PASS   |
| Execution timeout           | PASS   |
| Empty results               | PASS   |
| Partial results             | PASS   |

---

## 13. Troubleshooting

### Check Services

```bash
docker compose ps
```

### View Logs

```bash
docker compose logs -f
```

### Check OpenID Conformance Suite

```bash
curl -k -s -o /dev/null -w "%{http_code}\n" \
"https://localhost.emobix.co.uk:8443/api/plan?length=1"
```

### Check Certify

```bash
curl -s -o /dev/null -w "%{http_code}\n" \
"http://localhost:8090/v1/certify/.well-known/did.json"
```

### Check Verify

```bash
curl -s -o /dev/null -w "%{http_code}\n" \
"http://localhost:8080/v1/verify/actuator/health"
```

Expected healthy response:

```text
200
```

---

## 14. Project Structure

```text
mosip-decode-conformance/
│
├── .github/
│   └── workflows/
│       └── full-stack-conformance.yml
│
├── conformance-harness/
│   ├── configs/
│   │   ├── certify.json
│   │   └── verify.json
│   ├── reports/
│   │   └── benchmark.json
│   ├── runner/
│   │   ├── client.py
│   │   ├── executor.py
│   │   ├── results.py
│   │   └── test_plan.py
│   ├── main.py
│   └── requirements.txt
│
├── inji-certify/
├── inji-verify/
├── mosip-functional-tests/
├── conformance-suite/
│
├── docker-compose.yml
├── run-full-stack-conformance.sh
├── .gitignore
└── README.md
```

---

## Quick Reference

| Action       | Command                                               |
| ------------ | ----------------------------------------------------- |
| Start stack  | `docker compose up -d`                                |
| Run Certify  | `./run-full-stack-conformance.sh --component certify` |
| Run Verify   | `./run-full-stack-conformance.sh --component verify`  |
| Run Combined | `./run-full-stack-conformance.sh --combined`          |
| Run TestNG   | `mvn -Dtest=OpenIDConformanceTest test`               |
| Stop stack   | `docker compose down`                                 |

---

## Project Outcome

The project provides an automated, Dockerized, and CI/CD-ready workflow for executing OpenID conformance tests against **Inji Certify** and **Inji Verify**, integrating the execution with the **MOSIP `api-testrig`**, and detecting regressions through a benchmark gate.
