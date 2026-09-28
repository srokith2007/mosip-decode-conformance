#!/bin/bash

set -e

COMPONENT=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --component)
            COMPONENT="$2"
            shift 2
            ;;
        --combined)
            COMPONENT="combined"
            shift
            ;;
        *)
            echo "Unknown argument: $1"
            exit 1
            ;;
    esac
done

if [[ "$COMPONENT" != "certify" && "$COMPONENT" != "verify" && "$COMPONENT" != "combined" ]]; then
    echo "Usage:"
    echo "  ./run-full-stack-conformance.sh --component certify"
    echo "  ./run-full-stack-conformance.sh --component verify"
    echo "  ./run-full-stack-conformance.sh --combined"
    exit 1
fi

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "========================================"
echo " Starting full Docker environment"
echo "========================================"

cd "$PROJECT_ROOT"

docker compose -f docker-compose.yml up -d

echo ""
echo "Waiting for OpenID Conformance Suite..."

for i in {1..60}; do
    if curl -k -s -o /dev/null \
        "https://localhost.emobix.co.uk:8443/api/plan?length=1"; then
        echo "Conformance Suite is ready."
        break
    fi

    if [[ "$i" == "60" ]]; then
        echo "ERROR: Conformance Suite did not become ready."
        exit 1
    fi

    sleep 2
done

echo ""
echo "Waiting for Inji Certify..."

for i in {1..60}; do
    if curl -s -o /dev/null \
        "http://localhost:8090/v1/certify/.well-known/did.json"; then
        echo "Inji Certify is ready."
        break
    fi

    if [[ "$i" == "60" ]]; then
        echo "ERROR: Inji Certify did not become ready."
        exit 1
    fi

    sleep 2
done

echo ""
echo "Waiting for Inji Verify..."

for i in {1..60}; do
    if curl -s -o /dev/null \
        "http://localhost:8080/v1/verify/actuator/health"; then
        echo "Inji Verify is ready."
        break
    fi

    if [[ "$i" == "60" ]]; then
        echo "ERROR: Inji Verify did not become ready."
        exit 1
    fi

    sleep 2
done

echo ""
echo "========================================"
echo " Full environment is ready"
echo "========================================"

if [[ "$COMPONENT" == "combined" ]]; then

    echo ""
    echo "========================================"
    echo " Running combined api-testrig"
    echo "========================================"

    cd "$PROJECT_ROOT/mosip-functional-tests/apitest-commons"

    mvn -Dtest=OpenIDConformanceTest test

    echo ""
    echo "========================================"
    echo " FULL STACK CONFORMANCE PASSED"
    echo "========================================"

else

    cd "$PROJECT_ROOT/conformance-harness"

    echo ""
    echo "========================================"
    echo " Running $COMPONENT conformance"
    echo "========================================"

    python main.py --component "$COMPONENT"

fi
