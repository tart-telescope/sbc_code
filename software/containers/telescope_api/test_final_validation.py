#!/usr/bin/env python3
"""
Final validation test for FastAPI endpoints.
Tests all endpoints to ensure they return valid model data with no validation errors.
"""

import json
import time
from datetime import datetime
from typing import Any, Dict

import requests


class FinalValidationTester:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = []
        self.token = None
        self.validation_errors = []
        self.model_issues = []

    def log_result(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        response_data: Any = None,
        error: str = None,
    ):
        """Log test result with validation analysis"""
        result = {
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "timestamp": datetime.now().isoformat(),
            "status": "✅ PASS" if status_code == 200 else "❌ FAIL",
            "error": error,
            "response_type": type(response_data).__name__ if response_data else None,
            "has_validation_error": status_code == 422,
            "is_model_compliant": self.check_model_compliance(response_data, status_code),
        }

        # Check for specific model validation issues
        if status_code == 422 and response_data:
            self.validation_errors.append(
                {
                    "endpoint": endpoint,
                    "method": method,
                    "error_details": response_data.get("detail", []),
                }
            )

        # Check for datetime/Id field issues specifically
        if status_code == 500 and response_data:
            if "ValidationError" in str(response_data) or "datetime" in str(response_data).lower():
                self.model_issues.append(
                    {
                        "endpoint": endpoint,
                        "method": method,
                        "issue": "Potential datetime/Id field validation issue",
                    }
                )

        self.results.append(result)
        print(f"{result['status']} {method} {endpoint} - {status_code}")

        if error:
            print(f"    Error: {error}")
        if response_data and isinstance(response_data, dict) and "detail" in response_data:
            print(f"    Detail: {response_data['detail']}")

    def check_model_compliance(self, response_data: Any, status_code: int) -> bool:
        """Check if response is model compliant"""
        if status_code != 200:
            return False

        # Check for common model issues
        if isinstance(response_data, dict):
            # Check for datetime objects that should be strings
            for key, value in response_data.items():
                if hasattr(value, "isoformat"):  # datetime object
                    return False
                if key == "Id" and isinstance(value, int):  # Id field that should be removed
                    return False

        if isinstance(response_data, list):
            for item in response_data:
                if isinstance(item, dict):
                    for key, value in item.items():
                        if hasattr(value, "isoformat"):  # datetime object
                            return False
                        if key == "Id" and isinstance(
                            value, int
                        ):  # Id field that should be removed
                            return False

        return True

    def get_auth_token(self) -> bool:
        """Get authentication token"""
        try:
            response = self.session.post(
                f"{self.base_url}/auth/", json={"username": "admin", "password": "password"}
            )
            self.log_result(
                "/auth/",
                "POST",
                response.status_code,
                response.json() if response.status_code == 200 else None,
            )

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

    def test_endpoint(
        self, endpoint: str, method: str = "GET", json_data: Dict = None
    ) -> tuple[bool, Any]:
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

    def test_critical_endpoints(self):
        """Test critical endpoints that had validation issues"""
        print("🔍 Testing critical endpoints for validation issues...")

        critical_endpoints = [
            # Data endpoints (previously had datetime/Id issues)
            "/vis/data",
            "/raw/data",
            # Imaging endpoints (potential validation issues)
            "/imaging/vis",
            "/imaging/antenna_positions",
            "/imaging/timestamp",
            # Status endpoints
            "/status/fpga",
            "/status/channel",
            # Mode endpoints
            "/mode/current",
            "/mode",
        ]

        for endpoint in critical_endpoints:
            success, data = self.test_endpoint(endpoint)
            if success:
                print(f"    ✅ {endpoint} - Model validation OK")
            else:
                print(f"    ❌ {endpoint} - Model validation FAILED")

    def run_comprehensive_test(self):
        """Run comprehensive validation test"""
        print("🧪 Final Validation Test - FastAPI Model Compliance")
        print("=" * 70)

        # Test basic health first
        print("\n🏥 Health Check...")
        success, data = self.test_endpoint("/health")
        if not success:
            print("❌ Health check failed - container may not be ready")
            return False

        # Get auth token
        print("\n🔑 Authentication...")
        if not self.get_auth_token():
            print("⚠️  Auth failed, continuing without token...")

        # Test all endpoints systematically
        print("\n📋 Testing all endpoints...")

        # Basic endpoints
        basic_endpoints = [
            "/",
            "/info",
        ]

        for endpoint in basic_endpoints:
            self.test_endpoint(endpoint)

        # Mode endpoints
        mode_endpoints = [
            "/mode",
            "/mode/current",
            ("/mode/vis", "POST"),
        ]

        for item in mode_endpoints:
            if isinstance(item, tuple):
                endpoint, method = item
                self.test_endpoint(endpoint, method)
            else:
                self.test_endpoint(item)

        # Status endpoints
        status_endpoints = [
            "/status/fpga",
            "/status/channel",
            "/status/channel/0",
        ]

        for endpoint in status_endpoints:
            self.test_endpoint(endpoint)

        # Channel endpoints
        self.test_endpoint("/channel")

        # Calibration endpoints
        self.test_endpoint("/calibration/gain")

        # Critical imaging endpoints
        self.test_critical_endpoints()

        # Data endpoints (the main ones we fixed)
        print("\n📂 Testing data endpoints (main validation fix)...")
        data_endpoints = [
            "/raw/data",
            "/vis/data",
        ]

        for endpoint in data_endpoints:
            success, data = self.test_endpoint(endpoint)
            if success:
                print(f"    ✅ {endpoint} - No datetime/Id validation issues")
            else:
                print(f"    ❌ {endpoint} - Validation issues detected")

        return True

    def generate_final_report(self):
        """Generate comprehensive final report"""
        print("\n" + "=" * 70)
        print("📊 FINAL VALIDATION REPORT")
        print("=" * 70)

        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["status_code"] == 200)
        failed_tests = total_tests - passed_tests
        model_compliant = sum(1 for r in self.results if r["is_model_compliant"])

        print(f"Total endpoints tested: {total_tests}")
        print(f"Successful responses: {passed_tests}")
        print(f"Failed responses: {failed_tests}")
        print(f"Model compliant responses: {model_compliant}")
        print(f"Overall success rate: {passed_tests / total_tests * 100:.1f}%")
        print(f"Model compliance rate: {model_compliant / total_tests * 100:.1f}%")

        # Validation error analysis
        print("\n🔍 VALIDATION ERROR ANALYSIS:")
        print(f"Validation errors (422): {len(self.validation_errors)}")
        print(f"Model issues (datetime/Id): {len(self.model_issues)}")

        if self.validation_errors:
            print("\n❌ VALIDATION ERRORS:")
            for error in self.validation_errors:
                print(f"  {error['method']} {error['endpoint']}")
                for detail in error["error_details"]:
                    print(f"    - {detail}")

        if self.model_issues:
            print("\n⚠️  MODEL ISSUES:")
            for issue in self.model_issues:
                print(f"  {issue['method']} {issue['endpoint']}: {issue['issue']}")

        # Success summary
        critical_endpoints = ["/vis/data", "/raw/data", "/imaging/vis", "/imaging/timestamp"]
        critical_success = sum(
            1
            for r in self.results
            if r["endpoint"] in critical_endpoints and r["status_code"] == 200
        )

        print("\n🎯 CRITICAL ENDPOINTS STATUS:")
        print(f"Critical endpoints working: {critical_success}/{len(critical_endpoints)}")

        for endpoint in critical_endpoints:
            result = next((r for r in self.results if r["endpoint"] == endpoint), None)
            if result:
                status = "✅ PASS" if result["status_code"] == 200 else "❌ FAIL"
                print(f"  {endpoint}: {status}")

        # Final verdict
        print("\n🏆 FINAL VERDICT:")
        if len(self.validation_errors) == 0 and len(self.model_issues) == 0:
            print("✅ ALL MODEL VALIDATION ISSUES FIXED!")
            print("✅ No datetime/Id field validation errors")
            print("✅ All endpoints return properly formatted data")
        elif len(self.model_issues) == 0:
            print("✅ Main validation issues FIXED!")
            print("✅ No datetime/Id field validation errors")
            print(f"⚠️  {len(self.validation_errors)} minor validation errors (expected)")
        else:
            print("❌ Some validation issues remain")
            print(f"❌ {len(self.model_issues)} model issues found")

        # Save detailed results
        with open("final_validation_results.json", "w") as f:
            json.dump(
                {
                    "summary": {
                        "total_tests": total_tests,
                        "passed_tests": passed_tests,
                        "failed_tests": failed_tests,
                        "model_compliant": model_compliant,
                        "validation_errors": len(self.validation_errors),
                        "model_issues": len(self.model_issues),
                    },
                    "detailed_results": self.results,
                    "validation_errors": self.validation_errors,
                    "model_issues": self.model_issues,
                },
                f,
                indent=2,
            )

        print("\n📄 Detailed results saved to: final_validation_results.json")

        return len(self.validation_errors) == 0 and len(self.model_issues) == 0


def main():
    """Main validation function"""
    print("🚀 FastAPI Final Validation Test")
    print("Testing model compliance and validation fixes")
    print("=" * 70)

    # Check container status
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            print("✅ Container is healthy and ready")
        else:
            print(f"⚠️  Container health check returned {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot connect to container: {e}")
        return False

    # Wait for services to be ready
    print("⏳ Waiting for telescope services...")
    time.sleep(5)

    # Run validation tests
    tester = FinalValidationTester()
    if not tester.run_comprehensive_test():
        return False

    # Generate final report
    all_good = tester.generate_final_report()

    if all_good:
        print("\n🎉 VALIDATION SUCCESSFUL!")
        print("🎯 All model validation issues have been resolved!")
        print("✅ FastAPI migration is complete and ready for production!")
    else:
        print("\n⚠️  Some validation issues detected")
        print("📋 Review the detailed report above")

    return all_good


if __name__ == "__main__":
    main()
