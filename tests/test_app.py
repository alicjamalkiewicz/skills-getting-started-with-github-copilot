import pytest
from fastapi.testclient import TestClient
from src.app import app
import json

client = TestClient(app)

def test_get_activities():
    """Test getting all activities"""
    # Arrange - No special setup needed
    
    # Act
    response = client.get("/activities")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 9  # We have 9 activities
    
    # Check structure of one activity
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)

def test_signup_success():
    """Test successful signup"""
    # Arrange
    test_email = "test@example.com"
    activity = "Programming Class"
    response = client.get("/activities")
    initial_participants = response.json()[activity]["participants"]
    initial_count = len(initial_participants)
    
    # Act
    response = client.post(f"/activities/{activity}/signup", json={"email": test_email})
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert test_email in data["message"]
    
    # Verify participant was added
    response = client.get("/activities")
    updated_participants = response.json()[activity]["participants"]
    assert len(updated_participants) == initial_count + 1
    assert test_email in updated_participants

def test_signup_duplicate():
    """Test signing up twice fails"""
    # Arrange
    test_email = "duplicate@example.com"
    activity = "Programming Class"
    client.post(f"/activities/{activity}/signup", json={"email": test_email})  # First signup
    
    # Act
    response = client.post(f"/activities/{activity}/signup", json={"email": test_email})  # Second signup
    
    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"]

def test_signup_nonexistent_activity():
    """Test signing up for non-existent activity"""
    # Arrange - No special setup needed
    
    # Act
    response = client.post("/activities/NonExistent/signup", json={"email": "test@example.com"})
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]

def test_unregister_success():
    """Test successful unregister"""
    # Arrange
    test_email = "unregister@example.com"
    activity = "Gym Class"
    client.post(f"/activities/{activity}/signup", json={"email": test_email})  # Sign up first
    response = client.get("/activities")
    after_signup = response.json()[activity]["participants"]
    
    # Act
    response = client.request("DELETE", f"/activities/{activity}/signup", json={"email": test_email})
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Unregistered" in data["message"]
    
    # Verify participant was removed
    response = client.get("/activities")
    after_unregister = response.json()[activity]["participants"]
    assert len(after_unregister) == len(after_signup) - 1
    assert test_email not in after_unregister

def test_unregister_not_signed_up():
    """Test unregistering student not signed up"""
    # Arrange - No special setup needed
    
    # Act
    response = client.request("DELETE", "/activities/Chess Club/signup", json={"email": "notsignedup@example.com"})
    
    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "not signed up" in data["detail"]

def test_unregister_nonexistent_activity():
    """Test unregistering from non-existent activity"""
    # Arrange - No special setup needed
    
    # Act
    response = client.request("DELETE", "/activities/NonExistent/signup", json={"email": "test@example.com"})
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]

def test_root_redirect():
    """Test root endpoint redirects to static file"""
    # Arrange - No special setup needed
    
    # Act
    response = client.get("/")
    
    # Assert
    assert response.status_code == 200  # RedirectResponse, but TestClient follows redirects
    # Since it redirects to /static/index.html, and static files are mounted,
    # it should return the HTML content
    assert "Mergington High School" in response.text