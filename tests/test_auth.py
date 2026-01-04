"""
Authentication endpoint tests.
"""
import pytest
from httpx import AsyncClient


class TestRegister:
    """Tests for user registration"""

    @pytest.mark.asyncio
    async def test_register_with_email_success(self, client: AsyncClient, test_user_data):
        """Test successful registration with email"""
        response = await client.post("/api/v1/auth/register", json=test_user_data)

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["role"] == "student"
        assert data["is_active"] is True
        assert "id" in data

    @pytest.mark.asyncio
    async def test_register_with_phone_success(self, client: AsyncClient, test_user_phone_data):
        """Test successful registration with phone"""
        response = await client.post("/api/v1/auth/register", json=test_user_phone_data)

        assert response.status_code == 201
        data = response.json()
        assert data["phone"] == test_user_phone_data["phone"]
        assert data["role"] == "student"

    @pytest.mark.asyncio
    async def test_register_duplicate_email_fails(self, client: AsyncClient, test_user_data):
        """Test registration with duplicate email fails"""
        # First registration
        await client.post("/api/v1/auth/register", json=test_user_data)

        # Second registration with same email
        response = await client.post("/api/v1/auth/register", json=test_user_data)

        assert response.status_code == 409
        assert "already exists" in response.json()["message"].lower()

    @pytest.mark.asyncio
    async def test_register_short_password_fails(self, client: AsyncClient):
        """Test registration with short password fails"""
        response = await client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "short"
        })

        # Pydantic validation returns 422, domain validation returns 400
        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_register_no_email_or_phone_fails(self, client: AsyncClient):
        """Test registration without email or phone fails"""
        response = await client.post("/api/v1/auth/register", json={
            "password": "testpassword123"
        })

        # Pydantic validation returns 422, domain validation returns 400
        assert response.status_code in [400, 422]


class TestLogin:
    """Tests for user login"""

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, test_user_data):
        """Test successful login"""
        # Register first
        await client.post("/api/v1/auth/register", json=test_user_data)

        # Login
        response = await client.post("/api/v1/auth/login", json=test_user_data)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == test_user_data["email"]

    @pytest.mark.asyncio
    async def test_login_wrong_password_fails(self, client: AsyncClient, test_user_data):
        """Test login with wrong password fails"""
        # Register first
        await client.post("/api/v1/auth/register", json=test_user_data)

        # Login with wrong password
        response = await client.post("/api/v1/auth/login", json={
            "email": test_user_data["email"],
            "password": "wrongpassword"
        })

        assert response.status_code == 401
        assert "invalid" in response.json()["message"].lower()

    @pytest.mark.asyncio
    async def test_login_nonexistent_user_fails(self, client: AsyncClient):
        """Test login with nonexistent user fails"""
        response = await client.post("/api/v1/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "testpassword123"
        })

        assert response.status_code == 401


class TestRefreshToken:
    """Tests for token refresh"""

    @pytest.mark.asyncio
    async def test_refresh_token_success(self, client: AsyncClient, test_user_data):
        """Test successful token refresh"""
        # Register and login
        await client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await client.post("/api/v1/auth/login", json=test_user_data)
        refresh_token = login_response.json()["refresh_token"]

        # Refresh token
        response = await client.post("/api/v1/auth/refresh", json={
            "refresh_token": refresh_token
        })

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    @pytest.mark.asyncio
    async def test_refresh_invalid_token_fails(self, client: AsyncClient):
        """Test refresh with invalid token fails"""
        response = await client.post("/api/v1/auth/refresh", json={
            "refresh_token": "invalid-token"
        })

        assert response.status_code == 401


class TestGetCurrentUser:
    """Tests for getting current user"""

    @pytest.mark.asyncio
    async def test_get_me_success(self, client: AsyncClient, test_user_data):
        """Test getting current user profile"""
        # Register and login
        await client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await client.post("/api/v1/auth/login", json=test_user_data)
        access_token = login_response.json()["access_token"]

        # Get current user
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user_data["email"]

    @pytest.mark.asyncio
    async def test_get_me_unauthorized_fails(self, client: AsyncClient):
        """Test getting current user without token fails"""
        response = await client.get("/api/v1/auth/me")

        assert response.status_code in [401, 403]


class TestChangePassword:
    """Tests for changing password"""

    @pytest.mark.asyncio
    async def test_change_password_success(self, client: AsyncClient, test_user_data):
        """Test successful password change"""
        # Register and login
        await client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await client.post("/api/v1/auth/login", json=test_user_data)
        access_token = login_response.json()["access_token"]

        # Change password
        response = await client.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": test_user_data["password"],
                "new_password": "newpassword123"
            },
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 204

        # Verify old password no longer works
        response = await client.post("/api/v1/auth/login", json=test_user_data)
        assert response.status_code == 401

        # Verify new password works
        response = await client.post("/api/v1/auth/login", json={
            "email": test_user_data["email"],
            "password": "newpassword123"
        })
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_change_password_wrong_current_fails(self, client: AsyncClient, test_user_data):
        """Test password change with wrong current password fails"""
        # Register and login
        await client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await client.post("/api/v1/auth/login", json=test_user_data)
        access_token = login_response.json()["access_token"]

        # Try to change password with wrong current
        response = await client.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": "wrongpassword",
                "new_password": "newpassword123"
            },
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 401

