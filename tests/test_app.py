import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def reset_activities():
    """Reset activities to original state after each test"""
    original = activities.copy()
    yield
    activities.clear()
    activities.update(original)


class TestActivitiesAPI:
    """Test suite for Activities API endpoints"""

    def test_get_activities_success(self, reset_activities):
        """Test successful retrieval of all activities"""
        # Arrange
        client = TestClient(app)

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9  # Current number of activities
        assert "Chess Club" in data
        assert "participants" in data["Chess Club"]
        assert "max_participants" in data["Chess Club"]

    def test_root_redirect(self):
        """Test root endpoint redirects to static HTML"""
        # Arrange
        client = TestClient(app)

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307  # Temporary redirect
        assert response.headers["location"] == "/static/index.html"

    def test_signup_success(self, reset_activities):
        """Test successful signup for an activity"""
        # Arrange
        client = TestClient(app)
        activity = "Chess Club"
        email = "newstudent@mergington.edu"
        initial_count = len(activities[activity]["participants"])

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "Signed up" in result["message"]
        assert email in result["message"]
        assert email in activities[activity]["participants"]
        assert len(activities[activity]["participants"]) == initial_count + 1

    def test_signup_already_registered(self, reset_activities):
        """Test signup fails when student is already registered"""
        # Arrange
        client = TestClient(app)
        activity = "Chess Club"
        email = "michael@mergington.edu"  # Already registered

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 400
        result = response.json()
        assert "already signed up" in result["detail"]
        assert email in activities[activity]["participants"]  # Still registered

    def test_signup_nonexistent_activity(self, reset_activities):
        """Test signup fails for non-existent activity"""
        # Arrange
        client = TestClient(app)
        activity = "NonExistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "Activity not found" in result["detail"]

    def test_unregister_success(self, reset_activities):
        """Test successful unregister from an activity"""
        # Arrange
        client = TestClient(app)
        activity = "Chess Club"
        email = "michael@mergington.edu"  # Already registered
        initial_count = len(activities[activity]["participants"])

        # Act
        response = client.post(f"/activities/{activity}/unregister?email={email}")

        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "Unregistered" in result["message"]
        assert email not in activities[activity]["participants"]
        assert len(activities[activity]["participants"]) == initial_count - 1

    def test_unregister_not_registered(self, reset_activities):
        """Test unregister fails when student is not registered"""
        # Arrange
        client = TestClient(app)
        activity = "Chess Club"
        email = "notregistered@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity}/unregister?email={email}")

        # Assert
        assert response.status_code == 400
        result = response.json()
        assert "not signed up" in result["detail"]

    def test_unregister_nonexistent_activity(self, reset_activities):
        """Test unregister fails for non-existent activity"""
        # Arrange
        client = TestClient(app)
        activity = "NonExistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity}/unregister?email={email}")

        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "Activity not found" in result["detail"]