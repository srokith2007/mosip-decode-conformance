import sys
import asyncio
import json

sys.path.insert(0, r"..\conformance-suite\scripts")

from conformance import Conformance

async def main():
    conformance = Conformance(
        "https://localhost.emobix.co.uk:8443/",
        None,
        False
    )

    test_id = "XUOrqZ3Qd0YwbsK"

    info = await conformance.get_module_info(test_id)
    log = await conformance.get_test_log(test_id)

    print("\n=== TEST RESULT ===")
    print(json.dumps(info, indent=2))

    print("\n=== TEST LOG ===")
    print(json.dumps(log, indent=2))

    await conformance.close_client()

asyncio.run(main())
