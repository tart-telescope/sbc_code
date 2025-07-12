#!/usr/bin/env python3
"""
Test script for FastAPI endpoints running in Docker container.
Tests all endpoints and identifies any model validation issues.
"""

import json
import time
from datetime import datetime
from typing import Any, Dict

import requests


class EndpointTester:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = []
        self.token = None

    def log_result(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        response_data: Any = None,
        error: str = None,
    ):
        """Log test result"""
        result = {
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "timestamp": datetime.now().isoformat(),
            "status": "✅ PASS" if status_code == 200 else "❌ FAIL",
            "error": error,
            "response_preview": str(response_data)[:200] if response_data else None,
        }
        self.results.append(result)
        print(f"{result['status']} {method} {endpoint} - {status_code}")
        if error:
            print(f"    Error: {error}")
        if response_data and isinstance(response_data, dict) and "detail" in response_data:
            print(f"    Detail: {response_data['detail']}")

    def get_auth_token(self):
        """Get authentication token"""
        try:
            response = self.session.post(
                f"{self.base_url}/auth/", json={"username": "admin", "password": "password"}
            )
            self.log_result("/auth/", "POST", response.status_code)

            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                if self.token:
                    self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                return True
            return False
        except Exception as e:
            self.log_result("/auth/", "POST", 0, error=str(e))
            return False

    def test_endpoint(self, endpoint: str, method: str = "GET", json_data: Dict = None):
        """Test a single endpoint"""
        try:
            url = f"{self.base_url}{endpoint}"

            if method == "GET":
                response = self.session.get(url)
            elif method == "POST":
                response = self.session.post(url, json=json_data)
            elif method == "PUT":
                response = self.session.put(url, json=json_data)
            else:
                raise ValueError(f"Unsupported method: {method}")

            try:
                response_data = response.json()
            except:
                response_data = response.text

            self.log_result(endpoint, method, response.status_code, response_data)
            return response.status_code == 200, response_data

        except Exception as e:
            self.log_result(endpoint, method, 0, error=str(e))
            return False, None

    def test_all_endpoints(self):
        """Test all API endpoints"""
        print("🧪 Testing FastAPI endpoints in Docker container...")
        print("=" * 60)

        # Test basic endpoints (no auth required)
        basic_endpoints = [
            "/",
            "/health",
            "/info",
        ]

        for endpoint in basic_endpoints:
            self.test_endpoint(endpoint)

        # Get authentication token
        print("\n🔑 Getting authentication token...")
        if not self.get_auth_token():
            print("❌ Failed to get auth token, continuing without auth...")

        # Test auth endpoints
        auth_endpoints = [
            ("/auth/refresh", "POST", {"refresh_token": self.token}),
        ]

        for endpoint, method, data in auth_endpoints:
            self.test_endpoint(endpoint, method, data)

        # Test mode endpoints
        mode_endpoints = [
            "/mode",
            "/mode/current",
            ("/mode/off", "POST"),
            ("/mode/vis", "POST"),
        ]

        for item in mode_endpoints:
            if isinstance(item, tuple):
                endpoint, method = item
                self.test_endpoint(endpoint, method)
            else:
                self.test_endpoint(item)

        # Test loop endpoints
        loop_endpoints = [
            ("/loop/loop", "POST"),
            ("/loop/count/5", "POST"),
        ]

        for endpoint, method in loop_endpoints:
            self.test_endpoint(endpoint, method)

        # Test status endpoints
        status_endpoints = [
            "/status/fpga",
            "/status/channel",
            "/status/channel/0",
            "/status/channel/23",
        ]

        for endpoint in status_endpoints:
            self.test_endpoint(endpoint)

        # Test channel endpoints
        channel_endpoints = [
            "/channel",
            ("/channel/0/1", "PUT"),
            ("/channel/0/0", "PUT"),
        ]

        for item in channel_endpoints:
            if isinstance(item, tuple):
                endpoint, method = item
                self.test_endpoint(endpoint, method)
            else:
                self.test_endpoint(item)

        # Test calibration endpoints
        calibration_endpoints = [
            "/calibration/gain",
            ("/calibration/gain", "POST"),
            ("/calibration/antenna_positions", "POST"),
        ]

        for item in calibration_endpoints:
            if isinstance(item, tuple):
                endpoint, method = item
                self.test_endpoint(endpoint, method)
            else:
                self.test_endpoint(item)

        # Test imaging endpoints (these might have validation issues)
        print("\n📸 Testing imaging endpoints (checking for validation issues)...")
        imaging_endpoints = [
            "/imaging/vis",
            "/imaging/antenna_positions",
            "/imaging/timestamp",
        ]

        for endpoint in imaging_endpoints:
            success, data = self.test_endpoint(endpoint)
            if not success and data:
                print(f"    🔍 Validation issue detected: {data}")

        # Test acquisition endpoints
        acquisition_endpoints = [
            "/acquire/raw/save",
            "/acquire/vis/save",
            "/acquire/raw/num_samples_exp",
            "/acquire/vis/num_samples_exp",
            ("/acquire/raw/save/1", "PUT"),
            ("/acquire/vis/save/1", "PUT"),
            ("/acquire/raw/num_samples_exp/20", "PUT"),
            ("/acquire/vis/num_samples_exp/22", "PUT"),
        ]

        for item in acquisition_endpoints:
            if isinstance(item, tuple):
                endpoint, method = item
                self.test_endpoint(endpoint, method)
            else:
                self.test_endpoint(item)

        # Test data endpoints
        data_endpoints = [
            "/raw/data",
            "/vis/data",
        ]

        for endpoint in data_endpoints:
            self.test_endpoint(endpoint)

    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)

        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["status_code"] == 200)
        failed_tests = total_tests - passed_tests

        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success rate: {passed_tests / total_tests * 100:.1f}%")

        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.results:
                if result["status_code"] != 200:
                    print(f"  {result['method']} {result['endpoint']} - {result['status_code']}")
                    if result["error"]:
                        print(f"    Error: {result['error']}")

        # Check for specific validation issues
        print("\n🔍 VALIDATION ISSUE ANALYSIS:")
        validation_issues = []

        for result in self.results:
            if result["status_code"] == 422:  # Validation error
                validation_issues.append(result)

        if validation_issues:
            print(f"Found {len(validation_issues)} validation issues:")
            for issue in validation_issues:
                print(f"  {issue['endpoint']}: {issue.get('response_preview', 'Unknown error')}")
        else:
            print("No validation errors detected!")

        # Save detailed results
        with open("test_results_detailed.json", "w") as f:
            json.dump(self.results, f, indent=2)

        print("\n📄 Detailed results saved to: test_results_detailed.json")

        return passed_tests, failed_tests


def main():
    """Main test function"""
    print("🚀 FastAPI Docker Container Test Suite")
    print("Testing container at http://localhost:8001")
    print("=" * 60)

    # Check if container is running
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            print("✅ Container is running and healthy")
        else:
            print(f"⚠️  Container responded with status {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot connect to container: {e}")
        print("Make sure the container is running on port 8001")
        return

    # Wait a moment for services to initialize
    print("⏳ Waiting for services to initialize...")
    time.sleep(3)

    # Run tests
    tester = EndpointTester()
    tester.test_all_endpoints()
    passed, failed = tester.generate_report()

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! FastAPI migration is successful!")
    else:
        print(f"\n⚠️  {failed} tests failed. Check the issues above.")

    # Final check for specific visibility data
    print("\n🔍 Final visibility data check...")
    try:
        response = requests.get("http://localhost:8001/imaging/vis")
        if response.status_code == 200:
            data = response.json()
            print(f"Visibility data: {len(data.get('data', []))} entries")
            if data.get("data"):
                print(f"Sample entry: {data['data'][0]}")
        else:
            print(f"Visibility endpoint returned: {response.status_code}")
    except Exception as e:
        print(f"Error checking visibility data: {e}")


if __name__ == "__main__":
    main()
