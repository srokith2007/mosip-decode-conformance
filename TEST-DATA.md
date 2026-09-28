# Test Data

The project uses local Docker services and OpenID Conformance Suite test-plan configurations for automated conformance testing.

## Test Environment

* **Inji Certify:** Local Docker service
* **Inji Verify:** Local Docker service
* **OpenID Conformance Suite:** Local Docker deployment
* **Conformance Harness:** Python-based automation runner

## Test Configurations

### Certify

* Configuration: `conformance-harness/configs/certify.json`
* OpenID test plan: `oid4vci-1_0-issuer-haip-test-plan`
* Test endpoint: Local Inji Certify service

### Verify

* Configuration: `conformance-harness/configs/verify.json`
* OpenID test plan: `oid4vp-id3-verifier-test-plan`
* Test endpoint: Local Inji Verify service

## Credentials and Secrets

No real user credentials, production API keys, or production secrets are required.

Credentials configured in Docker Compose are development/test placeholder values used only for the local demonstration environment.

## Test Results

The repository includes automated test cases covering successful execution, failures, invalid configuration, service unavailability, network failures, timeouts, empty results, partial results, and benchmark regression detection.
