"""Tests for the Mergington High School Activities API."""

import pytest


class TestGetActivities:
    """Tests for the GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all activities."""
        response = client.get("/activities")
        
        assert response.status_code == 200
        activities = response.json()
        
        # Check that we have all activities
        assert len(activities) == 9
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities

    def test_get_activities_returns_correct_structure(self, client, reset_activities):
        """Test that each activity has the correct structure."""
        response = client.get("/activities")
        activities = response.json()
        
        chess_club = activities["Chess Club"]
        
        # Check structure
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)

    def test_get_activities_includes_initial_participants(self, client, reset_activities):
        """Test that activities include their initial participants."""
        response = client.get("/activities")
        activities = response.json()
        
        chess_club = activities["Chess Club"]
        assert len(chess_club["participants"]) == 2
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignup:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_successfully_adds_participant(self, client, reset_activities):
        """Test that a new participant can sign up for an activity."""
        response = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]

    def test_signup_actually_adds_participant_to_list(self, client, reset_activities):
        """Test that participant is actually added to the activity list."""
        # Sign up
        client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        
        # Verify participant was added
        response = client.get("/activities")
        activities = response.json()
        assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]
        assert len(activities["Chess Club"]["participants"]) == 3

    def test_signup_fails_for_nonexistent_activity(self, client, reset_activities):
        """Test that signup fails for a non-existent activity."""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_fails_if_already_registered(self, client, reset_activities):
        """Test that a student cannot sign up twice for the same activity."""
        # michael@mergington.edu is already in Chess Club
        response = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_with_special_characters_in_email(self, client, reset_activities):
        """Test that signup works with valid email formats."""
        response = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "student+test@mergington.edu"}
        )
        
        assert response.status_code == 200
        assert "student+test@mergington.edu" in response.json()["message"]

    def test_signup_multiple_students_different_activities(self, client, reset_activities):
        """Test that multiple students can sign up for different activities."""
        # Sign up first student
        response1 = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "student1@mergington.edu"}
        )
        assert response1.status_code == 200
        
        # Sign up second student to different activity
        response2 = client.post(
            "/activities/Programming%20Class/signup",
            params={"email": "student2@mergington.edu"}
        )
        assert response2.status_code == 200
        
        # Verify both were added
        response = client.get("/activities")
        activities = response.json()
        assert "student1@mergington.edu" in activities["Chess Club"]["participants"]
        assert "student2@mergington.edu" in activities["Programming Class"]["participants"]


class TestUnregister:
    """Tests for the POST /activities/{activity_name}/unregister endpoint."""

    def test_unregister_successfully_removes_participant(self, client, reset_activities):
        """Test that a participant can be unregistered from an activity."""
        response = client.post(
            "/activities/Chess%20Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "michael@mergington.edu" in data["message"]

    def test_unregister_actually_removes_participant_from_list(self, client, reset_activities):
        """Test that participant is actually removed from the activity list."""
        # Unregister
        client.post(
            "/activities/Chess%20Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        
        # Verify participant was removed
        response = client.get("/activities")
        activities = response.json()
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]
        assert len(activities["Chess Club"]["participants"]) == 1

    def test_unregister_fails_for_nonexistent_activity(self, client, reset_activities):
        """Test that unregister fails for a non-existent activity."""
        response = client.post(
            "/activities/Nonexistent%20Activity/unregister",
            params={"email": "student@mergington.edu"}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_unregister_fails_if_not_registered(self, client, reset_activities):
        """Test that unregister fails if the student is not registered."""
        response = client.post(
            "/activities/Chess%20Club/unregister",
            params={"email": "notregistered@mergington.edu"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"]

    def test_unregister_and_resign_up(self, client, reset_activities):
        """Test that a student can unregister and then sign up again."""
        # Unregister
        client.post(
            "/activities/Chess%20Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        
        # Verify they're no longer registered
        response = client.get("/activities")
        assert "michael@mergington.edu" not in response.json()["Chess Club"]["participants"]
        
        # Sign up again
        response = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 200
        
        # Verify they're back
        response = client.get("/activities")
        assert "michael@mergington.edu" in response.json()["Chess Club"]["participants"]

    def test_unregister_multiple_participants_from_same_activity(self, client, reset_activities):
        """Test that multiple participants can be unregistered."""
        # Unregister first participant
        response1 = client.post(
            "/activities/Chess%20Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        assert response1.status_code == 200
        
        # Unregister second participant
        response2 = client.post(
            "/activities/Chess%20Club/unregister",
            params={"email": "daniel@mergington.edu"}
        )
        assert response2.status_code == 200
        
        # Verify both were removed
        response = client.get("/activities")
        activities = response.json()
        assert len(activities["Chess Club"]["participants"]) == 0


class TestRootRedirect:
    """Tests for the root endpoint."""

    def test_root_redirects_to_static(self, client):
        """Test that the root endpoint redirects to static index."""
        response = client.get("/", follow_redirects=False)
        
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
