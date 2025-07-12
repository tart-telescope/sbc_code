#!/usr/bin/env python3
"""
Comprehensive endpoint test script for TART FastAPI application.

This script tests all 30 endpoints to verify they work correctly after migration.
"""

import json
import sys
from datetime import datetime
from typing import Any

import requests


class EndpointTester:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None
        self.results = []

    def log_result(
        self,
        endpoint: str,
        method: str,
        status: bool,
        response_code: int,
        error: str = None,
    ):
        """Log test result."""
        result = {
            "endpoint": endpoint,
            "method": method,
            "status": "✅ PASS" if status else "❌ FAIL",
            "response_code": response_code,
            "error": error,
            "timestamp": datetime.now().isoformat(),
        }
        self.results.append(result)

        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {method} {endpoint} ({response_code})")
        if error:
            print(f"   Error: {error}")

    def get_auth_token(self) -> bool:
        """Get authentication token."""
        try:
            response = self.session.post(
                f"{self.base_url}/auth/",
                json={"username": "admin", "password": "password"},
                timeout=10,
            )
            if response.status_code == 200:
                self.token = response.json()["access_token"]
                self.log_result("/auth/", "POST", True, response.status_code)
                return True
            else:
                self.log_result(
                    "/auth/", "POST", False, response.status_code, "Failed to get token"
                )
                return False
        except Exception as e:
            self.log_result("/auth/", "POST", False, 0, str(e))
            return False

    def test_endpoint(
        self,
        endpoint: str,
        method: str = "GET",
        auth_required: bool = False,
        data: dict[Any, Any] = None,
        expected_status: int = 200,
    ) -> bool:
        """Test a single endpoint."""
        try:
            headers = {}
            if auth_required and self.token:
                headers["Authorization"] = f"Bearer {self.token}"

            url = f"{self.base_url}{endpoint}"

            if method == "GET":
                response = self.session.get(url, headers=headers, timeout=10)
            elif method == "POST":
                response = self.session.post(
                    url, json=data, headers=headers, timeout=10
                )
            elif method == "PUT":
                response = self.session.put(url, json=data, headers=headers, timeout=10)
            else:
                self.log_result(
                    endpoint, method, False, 0, f"Unsupported method: {method}"
                )
                return False

            success = response.status_code == expected_status
            error = (
                None
                if success
                else f"Expected {expected_status}, got {response.status_code}"
            )

            self.log_result(endpoint, method, success, response.status_code, error)
            return success

        except Exception as e:
            self.log_result(endpoint, method, False, 0, str(e))
            return False

    def run_all_tests(self):
        """Run all endpoint tests."""
        print("🚀 Starting comprehensive endpoint tests...")
        print("=" * 60)

        # Basic endpoints (no auth required)
        print("\n📋 Testing basic endpoints...")
        self.test_endpoint("/")
        self.test_endpoint("/health")
        self.test_endpoint("/info")

        # Authentication
        print("\n🔐 Testing authentication...")
        if not self.get_auth_token():
            print("❌ Cannot continue without authentication token")
            return False

        self.test_endpoint("/auth/refresh", "POST", auth_required=True)

        # Mode and operation endpoints
        print("\n⚙️ Testing operation endpoints...")
        self.test_endpoint("/mode")
        self.test_endpoint("/mode/current")
        self.test_endpoint("/mode/off", "POST", auth_required=True)
        self.test_endpoint("/mode/vis", "POST", auth_required=True)
        self.test_endpoint("/loop/loop", "POST", auth_required=True)
        self.test_endpoint("/loop/count/5", "POST", auth_required=True)

        # Status endpoints
        print("\n📊 Testing status endpoints...")
        self.test_endpoint("/status/fpga")
        self.test_endpoint("/status/channel")
        self.test_endpoint("/status/channel/0")
        self.test_endpoint("/status/channel/23")

        # Channel management
        print("\n🔧 Testing channel endpoints...")
        self.test_endpoint("/channel")
        self.test_endpoint("/channel/0/1", "PUT", auth_required=True)
        self.test_endpoint("/channel/0/0", "PUT", auth_required=True)

        # Calibration endpoints
        print("\n🎯 Testing calibration endpoints...")
        self.test_endpoint("/calibration/gain")

        # Test setting gain (requires proper data structure)
        gain_data = {"gain": [1.0] * 24, "phase_offset": [0.0] * 24}
        self.test_endpoint(
            "/calibration/gain", "POST", auth_required=True, data=gain_data
        )

        # Test setting antenna positions
        antenna_data = {"antenna_positions": [[i, i, i] for i in range(24)]}
        self.test_endpoint(
            "/calibration/antenna_positions",
            "POST",
            auth_required=True,
            data=antenna_data,
        )

        # Imaging endpoints
        print("\n📸 Testing imaging endpoints...")
        self.test_endpoint("/imaging/vis")
        self.test_endpoint("/imaging/antenna_positions")
        self.test_endpoint("/imaging/timestamp")

        # Acquisition endpoints
        print("\n📥 Testing acquisition endpoints...")
        self.test_endpoint("/acquire/raw/save")
        self.test_endpoint("/acquire/vis/save")
        self.test_endpoint("/acquire/raw/num_samples_exp")
        self.test_endpoint("/acquire/vis/num_samples_exp")

        # Test setting acquisition parameters
        self.test_endpoint("/acquire/raw/save/1", "PUT", auth_required=True)
        self.test_endpoint("/acquire/vis/save/1", "PUT", auth_required=True)
        self.test_endpoint("/acquire/raw/num_samples_exp/20", "PUT", auth_required=True)
        self.test_endpoint("/acquire/vis/num_samples_exp/22", "PUT", auth_required=True)

        # Data endpoints
        print("\n📂 Testing data endpoints...")
        self.test_endpoint("/raw/data")
        self.test_endpoint("/vis/data")

        print("\n" + "=" * 60)
        self.print_summary()

    def print_summary(self):
        """Print test summary."""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if "PASS" in r["status"])
        failed_tests = total_tests - passed_tests

        print("📊 TEST SUMMARY")
        print(f"Total endpoints tested: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success rate: {(passed_tests / total_tests) * 100:.1f}%")

        if failed_tests > 0:
            print("\n❌ Failed endpoints:")
            for result in self.results:
                if "FAIL" in result["status"]:
                    print(
                        f"   {result['method']} {result['endpoint']} - {result['error']}"
                    )

        print(
            f"\n🎉 FastAPI Migration Status: {'SUCCESS' if failed_tests == 0 else 'NEEDS FIXES'}"
        )

        return failed_tests == 0

    def save_results(self, filename: str = "test_results.json"):
        """Save test results to JSON file."""
        with open(filename, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"📄 Results saved to {filename}")


def main():
    """Main test runner."""
    import argparse

    parser = argparse.ArgumentParser(description="Test TART FastAPI endpoints")
    parser.add_argument(
        "--url", default="http://localhost:8001", help="Base URL for API"
    )
    parser.add_argument("--save", action="store_true", help="Save results to JSON file")

    args = parser.parse_args()

    tester = EndpointTester(args.url)

    try:
        success = tester.run_all_tests()

        if args.save:
            tester.save_results()

        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test runner error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
