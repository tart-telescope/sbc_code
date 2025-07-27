"""
Comprehensive API test suite for TART Telescope API.

This test suite validates all API endpoints to ensure they work correctly
after the FastAPI migration from Flask.
"""

import os
import time

import pytest
import requests


class TARTAPITestClient:
    """Test client for TART Telescope API endpoints."""

    def __init__(self):
        self.base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
        self.username = os.getenv("TEST_USERNAME", "admin")
        self.password = os.getenv("TEST_PASSWORD", "password")
        self.token = None
        self.headers = {}
        self.original_state = {}

    def setup_method(self):
        """Set up test method - authenticate and save original state."""
        self.authenticate()
        self.save_original_state()

    def teardown_method(self):
        """Tear down test method - restore original state."""
        self.restore_original_state()
        self.ensure_all_antennas_enabled()

    def save_original_state(self):
        """Save original system state before test."""
        try:
            # Save original mode
            response = requests.get(f"{self.base_url}/mode/current")
            if response.status_code == 200:
                self.original_state["mode"] = response.json().get("mode")

            # Save original raw save flag
            response = requests.get(f"{self.base_url}/acquire/raw/save")
            if response.status_code == 200:
                self.original_state["raw_save"] = response.json().get("save")

            # Save original vis save flag
            response = requests.get(f"{self.base_url}/acquire/vis/save")
            if response.status_code == 200:
                self.original_state["vis_save"] = response.json().get("save")

            # Save original raw num samples exp
            response = requests.get(f"{self.base_url}/acquire/raw/num_samples_exp")
            if response.status_code == 200:
                self.original_state["raw_num_samples_exp"] = response.json().get("N_samples_exp")

            # Save original vis num samples exp
            response = requests.get(f"{self.base_url}/acquire/vis/num_samples_exp")
            if response.status_code == 200:
                self.original_state["vis_num_samples_exp"] = response.json().get("N_samples_exp")

            # Save original channel states
            response = requests.get(f"{self.base_url}/channel")
            if response.status_code == 200:
                self.original_state["channel_states"] = response.json()

        except Exception as e:
            print(f"Warning: Could not save original state: {e}")

    def restore_original_state(self):
        """Restore original system state after test."""
        try:
            # Restore original mode
            if "mode" in self.original_state:
                self.authenticate()
                requests.post(
                    f"{self.base_url}/mode/{self.original_state['mode']}",
                    headers=self.headers,
                )

            # Restore original raw save flag
            if "raw_save" in self.original_state:
                self.authenticate()
                requests.put(
                    f"{self.base_url}/acquire/raw/save/{self.original_state['raw_save']}",
                    headers=self.headers,
                )

            # Restore original vis save flag
            if "vis_save" in self.original_state:
                self.authenticate()
                requests.put(
                    f"{self.base_url}/acquire/vis/save/{self.original_state['vis_save']}",
                    headers=self.headers,
                )

            # Restore original raw num samples exp
            if "raw_num_samples_exp" in self.original_state:
                self.authenticate()
                requests.put(
                    f"{self.base_url}/acquire/raw/num_samples_exp/{self.original_state['raw_num_samples_exp']}",
                    headers=self.headers,
                )

            # Restore original vis num samples exp
            if "vis_num_samples_exp" in self.original_state:
                self.authenticate()
                requests.put(
                    f"{self.base_url}/acquire/vis/num_samples_exp/{self.original_state['vis_num_samples_exp']}",
                    headers=self.headers,
                )

        except Exception as e:
            print(f"Warning: Could not restore original state: {e}")

    def ensure_all_antennas_enabled(self):
        """Ensure all antennas/channels are enabled after tests."""
        try:
            self.authenticate()

            # Get current channel states
            response = requests.get(f"{self.base_url}/channel")
            if response.status_code == 200:
                channels = response.json()

                # Enable any disabled channels
                for channel in channels:
                    if channel["enabled"] == 0:
                        self.authenticate()
                        requests.put(
                            f"{self.base_url}/channel/{channel['channel_id']}/1",
                            headers=self.headers,
                        )
                        print(f"Re-enabled channel {channel['channel_id']}")

        except Exception as e:
            print(f"Warning: Could not ensure antennas are enabled: {e}")

    def authenticate(self):
        """Authenticate and get JWT token."""
        auth_data = {"username": self.username, "password": self.password}

        response = requests.post(f"{self.base_url}/auth", json=auth_data)
        assert response.status_code == 200, f"Authentication failed: {response.text}"

        token_data = response.json()
        self.token = token_data["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_health_check(self):
        """Test health check endpoint."""
        response = requests.get(f"{self.base_url}/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] in ["healthy", "degraded"]
        assert "telescope_service" in data
        assert data["telescope_service"]["service_running"] is True

    def test_root_endpoint(self):
        """Test root endpoint."""
        response = requests.get(f"{self.base_url}/")
        assert response.status_code == 200

        data = response.json()
        assert data["message"] == "TART Telescope API"
        assert data["status"] == "running"

    def test_info_endpoint(self):
        """Test telescope info endpoint."""
        response = requests.get(f"{self.base_url}/info")
        assert response.status_code == 200

        data = response.json()
        assert "info" in data
        info = data["info"]

        # Check required fields
        required_fields = [
            "name",
            "operating_frequency",
            "L0_frequency",
            "baseband_frequency",
            "sampling_frequency",
            "bandwidth",
            "num_antenna",
            "location",
        ]
        for field in required_fields:
            assert field in info, f"Missing field: {field}"

        # Check location structure
        location = info["location"]
        assert "lon" in location
        assert "lat" in location
        assert "alt" in location

    def test_authentication_flow(self):
        """Test authentication endpoints."""
        # Test successful authentication
        auth_data = {"username": self.username, "password": self.password}

        response = requests.post(f"{self.base_url}/auth", json=auth_data)
        assert response.status_code == 200

        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

        # Test refresh token
        refresh_headers = {"Authorization": f"Bearer {data['refresh_token']}"}
        response = requests.post(f"{self.base_url}/auth/refresh", headers=refresh_headers)
        assert response.status_code == 200

        refresh_data = response.json()
        assert "access_token" in refresh_data

        # Test invalid credentials
        bad_auth_data = {"username": "invalid", "password": "invalid"}

        response = requests.post(f"{self.base_url}/auth", json=bad_auth_data)
        assert response.status_code == 401

    def test_mode_operations(self):
        """Test telescope mode operations."""
        # Get available modes
        response = requests.get(f"{self.base_url}/mode")
        assert response.status_code == 200

        data = response.json()
        assert "modes" in data
        available_modes = data["modes"]
        assert isinstance(available_modes, list)
        assert len(available_modes) > 0

        # Get current mode
        response = requests.get(f"{self.base_url}/mode/current")
        assert response.status_code == 200

        data = response.json()
        assert "mode" in data
        data["mode"]

        # Test mode switching
        test_modes = ["off", "diag"]  # Test fewer modes to reduce interference
        for mode in test_modes:
            if mode in available_modes:
                self.authenticate()
                response = requests.post(f"{self.base_url}/mode/{mode}", headers=self.headers)
                assert response.status_code == 200

                data = response.json()
                assert data["mode"] == mode

                # Verify mode changed
                response = requests.get(f"{self.base_url}/mode/current")
                assert response.status_code == 200

                data = response.json()
                assert data["mode"] == mode

                # Small delay to allow state machine to process
                time.sleep(0.5)

        # Note: Original mode will be restored in teardown_method

    def test_loop_operations(self):
        """Test telescope loop operations."""
        # Test loop mode setting (test only one to avoid interference)
        loop_modes = ["loop"]

        for loop_mode in loop_modes:
            self.authenticate()
            response = requests.post(f"{self.base_url}/loop/{loop_mode}", headers=self.headers)
            assert response.status_code == 200

            data = response.json()
            assert "loop_mode" in data

        # Test loop count setting
        self.authenticate()
        response = requests.post(f"{self.base_url}/loop/count/5", headers=self.headers)
        assert response.status_code == 200

        data = response.json()
        assert "loop_mode" in data

    def test_acquisition_endpoints(self):
        """Test data acquisition endpoints."""
        # Test raw data save flag
        response = requests.get(f"{self.base_url}/acquire/raw/save")
        assert response.status_code == 200

        data = response.json()
        assert "save" in data
        original_save = data["save"]

        # Test setting save flag
        new_save = 1 if original_save == 0 else 0
        self.authenticate()
        response = requests.put(
            f"{self.base_url}/acquire/raw/save/{new_save}", headers=self.headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["save"] == new_save

        # Verify the change took effect
        response = requests.get(f"{self.base_url}/acquire/raw/save")
        assert response.status_code == 200
        data = response.json()
        assert data["save"] == new_save

        # Note: Original value will be restored in teardown_method

        # Test visibility data save flag
        response = requests.get(f"{self.base_url}/acquire/vis/save")
        assert response.status_code == 200

        data = response.json()
        assert "save" in data

        # Test sample exponent settings
        response = requests.get(f"{self.base_url}/acquire/raw/num_samples_exp")
        assert response.status_code == 200

        data = response.json()
        assert "N_samples_exp" in data
        data["N_samples_exp"]

        # Test setting valid exponent
        test_exp = 20
        self.authenticate()
        response = requests.put(
            f"{self.base_url}/acquire/raw/num_samples_exp/{test_exp}",
            headers=self.headers,
        )
        assert response.status_code == 200

        data = response.json()
        assert data["N_samples_exp"] == test_exp

        # Note: Original value will be restored in teardown_method

    def test_calibration_endpoints(self):
        """Test calibration endpoints."""
        # Test get gain
        response = requests.get(f"{self.base_url}/calibration/gain")
        assert response.status_code == 200

        data = response.json()
        assert "gain" in data
        assert "phase_offset" in data

        # Test antenna positions
        response = requests.get(f"{self.base_url}/imaging/antenna_positions")
        assert response.status_code == 200

        data = response.json()
        # Data is returned as a list directly, not wrapped in "positions"
        assert isinstance(data, list)
        assert len(data) > 0

    def test_imaging_endpoints(self):
        """Test imaging endpoints."""
        # Test get latest visibilities
        response = requests.get(f"{self.base_url}/imaging/vis")
        assert response.status_code == 200

        # Response might be empty if no data available, but should not error
        data = response.json()
        # The response structure depends on whether vis_current is available

        # Test antenna positions
        response = requests.get(f"{self.base_url}/imaging/antenna_positions")
        assert response.status_code == 200

        data = response.json()
        # Data is returned as a list directly, not wrapped in "positions"
        assert isinstance(data, list)

        # Test timestamp - may return 404 if no visibility data available
        response = requests.get(f"{self.base_url}/imaging/timestamp")
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            # If we have visibility data, should return a valid ISO timestamp string
            timestamp = response.json()
            assert isinstance(timestamp, str)
            # Should be a valid ISO timestamp format (ends with Z or timezone offset)
            assert timestamp.endswith("Z") or ("+" in timestamp[-6:] or "-" in timestamp[-6:])
        else:
            # If no visibility data, should return 404 with error message
            error_data = response.json()
            assert "detail" in error_data

    def test_channel_endpoints(self):
        """Test channel management endpoints."""
        # Test get all channels
        response = requests.get(f"{self.base_url}/channel")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

        # Test channel toggle (if channels exist)
        if len(data) > 0:
            # Test enabling/disabling first channel
            self.authenticate()
            response = requests.put(f"{self.base_url}/channel/0/1", headers=self.headers)
            assert response.status_code == 200

            self.authenticate()
            response = requests.put(f"{self.base_url}/channel/0/0", headers=self.headers)
            assert response.status_code == 200

            # Always re-enable the channel after testing
            self.authenticate()
            response = requests.put(f"{self.base_url}/channel/0/1", headers=self.headers)
            assert response.status_code == 200

    def test_data_endpoints(self):
        """Test data retrieval endpoints."""
        # Test raw data files
        response = requests.get(f"{self.base_url}/raw/data")
        assert response.status_code == 200

        data = response.json()
        # Data might be empty in development, but should be a list
        assert isinstance(data, list)

        # Test visibility data files
        response = requests.get(f"{self.base_url}/vis/data")
        assert response.status_code == 200

        data = response.json()
        # Data might be empty in development, but should be a list
        assert isinstance(data, list)

    def test_unauthorized_access(self):
        """Test that protected endpoints require authentication."""
        protected_endpoints = [
            ("POST", "/mode/off"),
            ("POST", "/loop/loop"),
            ("PUT", "/acquire/raw/save/1"),
            ("PUT", "/channel/0/1"),
            ("POST", "/calibration/gain"),
        ]

        for method, endpoint in protected_endpoints:
            if method == "POST":
                response = requests.post(f"{self.base_url}{endpoint}")
            elif method == "PUT":
                response = requests.put(f"{self.base_url}{endpoint}")

            assert response.status_code == 401, f"Endpoint {endpoint} should require authentication"

    def test_openapi_docs(self):
        """Test that OpenAPI documentation is accessible."""
        # Test OpenAPI JSON
        response = requests.get(f"{self.base_url}/openapi.json")
        assert response.status_code == 200

        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data

        # Test Swagger UI
        response = requests.get(f"{self.base_url}/docs")
        assert response.status_code == 200
        assert "swagger" in response.text.lower()

        # Test ReDoc
        response = requests.get(f"{self.base_url}/redoc")
        assert response.status_code == 200
        assert "redoc" in response.text.lower()

    def test_error_handling(self):
        """Test error handling for invalid requests."""
        # Test invalid mode
        self.authenticate()
        response = requests.post(f"{self.base_url}/mode/invalid_mode", headers=self.headers)
        assert response.status_code == 422  # Validation error

        # Test invalid channel
        self.authenticate()
        response = requests.put(f"{self.base_url}/channel/999/1", headers=self.headers)
        assert response.status_code in [
            200,
            400,
            404,
            422,
        ]  # 200 might be returned for invalid channels

        # Test invalid sample exponent
        response = requests.put(
            f"{self.base_url}/acquire/raw/num_samples_exp/999", headers=self.headers
        )
        assert response.status_code == 200  # Should be silently ignored based on logic

        # Test nonexistent endpoint
        response = requests.get(f"{self.base_url}/nonexistent")
        assert response.status_code == 404

    def test_visibility_data_collection(self):
        """Test that visibility data is collected when telescope is in vis mode."""
        # Set telescope to vis mode
        self.authenticate()
        response = requests.post(f"{self.base_url}/mode/vis", headers=self.headers)
        assert response.status_code == 200
        assert response.json()["mode"] == "vis"

        # Wait for visibility data collection (at least 3 seconds)
        time.sleep(3)

        # Check that visibility data is available
        response = requests.get(f"{self.base_url}/imaging/vis")
        assert response.status_code == 200

        data = response.json()
        assert "data" in data

        # Should have visibility data after being in vis mode
        assert len(data["data"]) > 0, "No visibility data collected after 3 seconds in vis mode"

        # Check data structure
        if data["data"]:
            vis_sample = data["data"][0]
            # Visibility data should have i, j, and re/im components
            required_fields = ["i", "j"]
            for field in required_fields:
                assert field in vis_sample, f"Missing field {field} in visibility data"

    def test_antenna_management(self):
        """Test that antennas can be disabled and re-enabled properly."""
        # Get current channel states
        response = requests.get(f"{self.base_url}/channel")
        assert response.status_code == 200

        original_channels = response.json()
        assert len(original_channels) > 0

        # Disable a few channels
        test_channels = [1, 2, 3]

        for channel_id in test_channels:
            self.authenticate()
            response = requests.put(f"{self.base_url}/channel/{channel_id}/0", headers=self.headers)
            assert response.status_code == 200

        # Verify they are disabled
        response = requests.get(f"{self.base_url}/channel")
        assert response.status_code == 200

        current_channels = response.json()
        for channel in current_channels:
            if channel["channel_id"] in test_channels:
                assert channel["enabled"] == 0, (
                    f"Channel {channel['channel_id']} should be disabled"
                )

        # Re-enable all channels
        for channel_id in test_channels:
            self.authenticate()
            response = requests.put(f"{self.base_url}/channel/{channel_id}/1", headers=self.headers)
            assert response.status_code == 200

        # Verify they are enabled
        response = requests.get(f"{self.base_url}/channel")
        assert response.status_code == 200

        final_channels = response.json()
        for channel in final_channels:
            if channel["channel_id"] in test_channels:
                assert channel["enabled"] == 1, (
                    f"Channel {channel['channel_id']} should be re-enabled"
                )

    def test_antenna_positions_persistence(self):
        """Test that antenna positions set via calibration route persist when retrieved via imaging route."""
        # First, get the original antenna positions from imaging route
        response = requests.get(f"{self.base_url}/imaging/antenna_positions")
        assert response.status_code == 200
        original_positions = response.json()
        assert isinstance(original_positions, list)
        assert len(original_positions) > 0

        # Create modified antenna positions (shift all by small amount)
        modified_positions = []
        for pos in original_positions:
            modified_positions.append([pos[0] + 0.001, pos[1] + 0.001, pos[2] + 0.001])

        # Set new antenna positions via calibration route
        self.authenticate()
        payload = {"antenna_positions": modified_positions}
        response = requests.post(
            f"{self.base_url}/calibration/antenna_positions", json=payload, headers=self.headers
        )
        assert response.status_code == 200

        # Wait a brief moment for the config to propagate
        import time

        time.sleep(0.5)

        # Retrieve antenna positions via imaging route
        response = requests.get(f"{self.base_url}/imaging/antenna_positions")
        assert response.status_code == 200
        retrieved_positions = response.json()

        # Verify the positions match what we set
        assert len(retrieved_positions) == len(modified_positions)
        for i, (set_pos, retrieved_pos) in enumerate(zip(modified_positions, retrieved_positions)):
            for j, (set_coord, retrieved_coord) in enumerate(zip(set_pos, retrieved_pos)):
                assert abs(set_coord - retrieved_coord) < 1e-10, (
                    f"Position mismatch at antenna {i}, coordinate {j}: "
                    f"set {set_coord}, retrieved {retrieved_coord}"
                )

        # Restore original positions
        self.authenticate()
        payload = {"antenna_positions": original_positions}
        response = requests.post(
            f"{self.base_url}/calibration/antenna_positions", json=payload, headers=self.headers
        )
        assert response.status_code == 200

    def test_antenna_positions_formats(self):
        """Test that both new and legacy antenna positions formats are accepted."""
        # Get original positions
        response = requests.get(f"{self.base_url}/imaging/antenna_positions")
        assert response.status_code == 200
        original_positions = response.json()

        # Test new format: {"antenna_positions": [...]}
        self.authenticate()
        new_format_payload = {"antenna_positions": [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]}
        response = requests.post(
            f"{self.base_url}/calibration/antenna_positions",
            json=new_format_payload,
            headers=self.headers,
        )
        assert response.status_code == 200

        # Verify new format was set
        response = requests.get(f"{self.base_url}/imaging/antenna_positions")
        assert response.status_code == 200
        retrieved_positions = response.json()
        assert retrieved_positions == [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]

        # Test legacy format: [[1,2,3],[4,5,6],...]
        self.authenticate()
        legacy_format_payload = [[7.0, 8.0, 9.0], [10.0, 11.0, 12.0]]
        response = requests.post(
            f"{self.base_url}/calibration/antenna_positions",
            json=legacy_format_payload,
            headers=self.headers,
        )
        assert response.status_code == 200

        # Verify legacy format was set
        response = requests.get(f"{self.base_url}/imaging/antenna_positions")
        assert response.status_code == 200
        retrieved_positions = response.json()
        assert retrieved_positions == [[7.0, 8.0, 9.0], [10.0, 11.0, 12.0]]

        # Restore original positions
        self.authenticate()
        restore_payload = {"antenna_positions": original_positions}
        response = requests.post(
            f"{self.base_url}/calibration/antenna_positions",
            json=restore_payload,
            headers=self.headers,
        )
        assert response.status_code == 200


# Fixture for the test class
@pytest.fixture
def api_client():
    """Create API client for testing."""
    return TARTAPITestClient()


# Test functions that use the fixture
def test_health_check(api_client):
    api_client.test_health_check()


def test_root_endpoint(api_client):
    api_client.test_root_endpoint()


def test_info_endpoint(api_client):
    api_client.test_info_endpoint()


def test_authentication_flow(api_client):
    api_client.test_authentication_flow()


def test_mode_operations(api_client):
    api_client.test_mode_operations()


def test_loop_operations(api_client):
    api_client.test_loop_operations()


def test_acquisition_endpoints(api_client):
    api_client.test_acquisition_endpoints()


def test_calibration_endpoints(api_client):
    api_client.test_calibration_endpoints()


def test_imaging_endpoints(api_client):
    api_client.test_imaging_endpoints()


def test_channel_endpoints(api_client):
    api_client.test_channel_endpoints()


def test_data_endpoints(api_client):
    api_client.test_data_endpoints()


def test_unauthorized_access(api_client):
    api_client.test_unauthorized_access()


def test_openapi_docs(api_client):
    api_client.test_openapi_docs()


def test_error_handling(api_client):
    api_client.test_error_handling()


def test_visibility_data_collection(api_client):
    api_client.test_visibility_data_collection()


def test_antenna_management(api_client):
    api_client.test_antenna_management()


def test_antenna_positions_persistence(api_client):
    api_client.test_antenna_positions_persistence()


def test_antenna_positions_formats(api_client):
    api_client.test_antenna_positions_formats()
