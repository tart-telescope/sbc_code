#!/usr/bin/env python3
"""
Detailed validation test script for TART FastAPI endpoints.
This script tests response data validation and identifies any model validation issues.
"""

import json
import time
import traceback
from datetime import datetime
from typing import Any

import requests

# Test configuration
BASE_URL = "http://localhost:8001"
TIMEOUT = 10


def test_endpoint_validation(
    endpoint: str, method: str = "GET", data: dict = None, auth_token: str = None
) -> dict[str, Any]:
    """Test an endpoint and return detailed validation information."""
    headers = {}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"

    try:
        if method == "GET":
            response = requests.get(
                f"{BASE_URL}{endpoint}", headers=headers, timeout=TIMEOUT
            )
        elif method == "POST":
            response = requests.post(
                f"{BASE_URL}{endpoint}", json=data, headers=headers, timeout=TIMEOUT
            )
        elif method == "PUT":
            response = requests.put(
                f"{BASE_URL}{endpoint}", json=data, headers=headers, timeout=TIMEOUT
            )
        else:
            return {"error": f"Unsupported method: {method}"}

        result = {
            "endpoint": endpoint,
            "method": method,
            "status_code": response.status_code,
            "success": response.status_code == 200,
            "response_size": len(response.text),
            "content_type": response.headers.get("content-type", ""),
            "raw_response": response.text[:500] + "..."
            if len(response.text) > 500
            else response.text,
        }

        # Try to parse JSON
        try:
            json_data = response.json()
            result["json_valid"] = True
            result["json_data"] = json_data
            result["data_type"] = type(json_data).__name__

            # Check for specific validation patterns
            if isinstance(json_data, dict):
                result["keys"] = list(json_data.keys())
                if "data" in json_data:
                    result["data_length"] = (
                        len(json_data["data"])
                        if isinstance(json_data["data"], list)
                        else 1
                    )
                    if (
                        isinstance(json_data["data"], list)
                        and len(json_data["data"]) > 0
                    ):
                        result["sample_data_item"] = json_data["data"][0]
            elif isinstance(json_data, list):
                result["list_length"] = len(json_data)
                if len(json_data) > 0:
                    result["sample_item"] = json_data[0]

        except json.JSONDecodeError as e:
            result["json_valid"] = False
            result["json_error"] = str(e)

    except Exception as e:
        result = {
            "endpoint": endpoint,
            "method": method,
            "error": str(e),
            "traceback": traceback.format_exc(),
            "success": False,
        }

    return result


def get_auth_token() -> str:
    """Get authentication token for protected endpoints."""
    try:
        response = requests.post(
            f"{BASE_URL}/auth/",
            json={"username": "admin", "password": "password"},
            timeout=TIMEOUT,
        )
        if response.status_code == 200:
            return response.json().get("access_token", "")
    except Exception as e:
        print(f"Failed to get auth token: {e}")
    return ""


def main():
    """Run comprehensive validation tests."""
    print("🔍 Starting detailed validation tests...")
    print("=" * 80)

    # Get auth token
    auth_token = get_auth_token()
    print(f"🔑 Auth token: {'✅ Obtained' if auth_token else '❌ Failed'}")
    print()

    # Test endpoints with detailed validation
    test_cases = [
        # Basic endpoints
        ("/", "GET"),
        ("/health", "GET"),
        ("/info", "GET"),
        # Auth endpoints
        ("/auth/", "POST", {"username": "admin", "password": "password"}),
        # Status endpoints
        ("/status/fpga", "GET"),
        ("/status/channel", "GET"),
        ("/status/channel/0", "GET"),
        # Channel endpoints
        ("/channel", "GET"),
        # Calibration endpoints
        ("/calibration/gain", "GET"),
        # Imaging endpoints (potentially problematic)
        ("/imaging/vis", "GET"),
        ("/imaging/antenna_positions", "GET"),
        ("/imaging/timestamp", "GET"),
        # Data endpoints
        ("/raw/data", "GET"),
        ("/vis/data", "GET"),
        # Operation endpoints
        ("/mode", "GET"),
        ("/mode/current", "GET"),
    ]

    results = []
    issues = []

    for test_case in test_cases:
        endpoint = test_case[0]
        method = test_case[1]
        data = test_case[2] if len(test_case) > 2 else None

        print(f"🧪 Testing {method} {endpoint}...")

        # Use auth token for protected endpoints (most of them)
        use_auth = endpoint not in ["/", "/health", "/info", "/auth/"]
        token = auth_token if use_auth else None

        result = test_endpoint_validation(endpoint, method, data, token)
        results.append(result)

        if result.get("success"):
            print(f"   ✅ Status: {result['status_code']}")
            print(
                f"   📊 Response: {result['data_type']} ({result['response_size']} bytes)"
            )

            if "keys" in result:
                print(f"   🔑 Keys: {result['keys']}")

            if "data_length" in result:
                print(f"   📋 Data items: {result['data_length']}")

            if "sample_data_item" in result:
                print(
                    f"   🔍 Sample: {json.dumps(result['sample_data_item'], indent=2)[:200]}..."
                )

            if "list_length" in result:
                print(f"   📏 List length: {result['list_length']}")

            if "sample_item" in result:
                print(
                    f"   🔍 Sample: {json.dumps(result['sample_item'], indent=2)[:200]}..."
                )

        else:
            print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
            issues.append(f"{endpoint}: {result.get('error', 'Unknown error')}")

        print()
        time.sleep(0.1)  # Small delay to avoid overwhelming the server

    # Summary
    print("=" * 80)
    print("📊 VALIDATION SUMMARY")
    print("=" * 80)

    successful = sum(1 for r in results if r.get("success"))
    total = len(results)

    print(f"Total endpoints tested: {total}")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {total - successful}")
    print(f"Success rate: {(successful / total) * 100:.1f}%")

    if issues:
        print("\n🚨 ISSUES FOUND:")
        for issue in issues:
            print(f"   - {issue}")

    # Check for specific validation patterns
    print("\n🔍 DETAILED ANALYSIS:")

    # Check visibility data
    vis_result = next((r for r in results if r.get("endpoint") == "/imaging/vis"), None)
    if vis_result and vis_result.get("success"):
        vis_data = vis_result.get("json_data", {})
        if isinstance(vis_data, dict) and "data" in vis_data:
            data_items = vis_data["data"]
            print(f"   📸 Visibility data: {len(data_items)} items")
            if len(data_items) > 0:
                sample_item = data_items[0]
                print(
                    f"   🔍 Sample visibility item: {json.dumps(sample_item, indent=2)}"
                )

                # Check for validation issues in sample item
                if isinstance(sample_item, dict):
                    if "Id" in sample_item:
                        print(
                            "   ⚠️  Found 'Id' field (should be lowercase 'id' or removed)"
                        )
                    if "timestamp" in sample_item:
                        ts_value = sample_item["timestamp"]
                        if isinstance(ts_value, str):
                            print(f"   ✅ Timestamp is string: {ts_value}")
                        else:
                            print(
                                f"   ⚠️  Timestamp is not string: {type(ts_value)} - {ts_value}"
                            )
            else:
                print(
                    "   ℹ️  No visibility data items (expected if no data captured yet)"
                )

    # Check file data endpoints
    for endpoint in ["/raw/data", "/vis/data"]:
        result = next((r for r in results if r.get("endpoint") == endpoint), None)
        if result and result.get("success"):
            data = result.get("json_data", [])
            if isinstance(data, list) and len(data) > 0:
                sample_file = data[0]
                print(
                    f"   📁 {endpoint} sample file: {json.dumps(sample_file, indent=2)}"
                )

                # Check FileHandle model fields
                if isinstance(sample_file, dict):
                    required_fields = ["filename", "checksum", "timestamp"]
                    for field in required_fields:
                        if field not in sample_file:
                            print(
                                f"   ⚠️  Missing required field '{field}' in {endpoint}"
                            )
                        else:
                            value = sample_file[field]
                            if field == "timestamp" and not isinstance(value, str):
                                print(
                                    f"   ⚠️  Timestamp should be string, got {type(value)}: {value}"
                                )

    print("\n🎯 VALIDATION COMPLETE!")

    # Save detailed results
    with open("validation_results.json", "w") as f:
        json.dump(
            {
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total": total,
                    "successful": successful,
                    "failed": total - successful,
                    "success_rate": (successful / total) * 100,
                },
                "issues": issues,
                "results": results,
            },
            f,
            indent=2,
            default=str,
        )

    print("💾 Detailed results saved to validation_results.json")


if __name__ == "__main__":
    main()
