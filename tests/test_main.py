"""Unit tests for main Flask application."""

from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import pytest

from main import app, fetch_reviews, get_connection, render_reviews_page


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestGetConnection:
    """Tests for database connection logic."""

    @patch("main.psycopg2.connect")
    def test_get_connection_success_first_attempt(self, mock_connect):
        """Test successful connection on first attempt."""
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        conn = get_connection()

        assert conn == mock_conn
        mock_connect.assert_called_once()

    @patch("main.psycopg2.connect")
    @patch("main.time.sleep")
    def test_get_connection_retry_then_success(self, mock_sleep, mock_connect):
        """Test connection retry and eventual success."""
        mock_conn = MagicMock()
        # Fail twice, then succeed
        mock_connect.side_effect = [
            Exception("Connection refused"),
            Exception("Connection refused"),
            mock_conn,
        ]

        conn = get_connection(max_attempts=3, delay_seconds=1)

        assert conn == mock_conn
        assert mock_connect.call_count == 3
        assert mock_sleep.call_count == 2

    @patch("main.psycopg2.connect")
    def test_get_connection_failure_all_attempts(self, mock_connect):
        """Test connection fails after all attempts."""
        mock_connect.side_effect = Exception("Connection refused")

        with pytest.raises(Exception, match="Connection refused"):
            get_connection(max_attempts=2, delay_seconds=1)

        assert mock_connect.call_count == 2

    @patch.dict("os.environ", {"DB_HOST": "custom-host", "DB_PORT": "5555"})
    @patch("main.psycopg2.connect")
    def test_get_connection_environment_variables(self, mock_connect):
        """Test that environment variables are used correctly."""
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        get_connection()

        mock_connect.assert_called_once()
        call_kwargs = mock_connect.call_args[1]
        assert call_kwargs["host"] == "custom-host"
        assert call_kwargs["port"] == 5555

    @patch.dict("os.environ", {}, clear=True)
    @patch("main.psycopg2.connect")
    def test_get_connection_default_values(self, mock_connect):
        """Test default values when environment variables are not set."""
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        get_connection()

        call_kwargs = mock_connect.call_args[1]
        assert call_kwargs["host"] == "localhost"
        assert call_kwargs["port"] == 5432
        assert call_kwargs["dbname"] == "moviereviews"
        assert call_kwargs["user"] == "appuser"
        assert call_kwargs["password"] == "apppass"


class TestFetchReviews:
    """Tests for review fetching."""

    @patch("main.get_connection")
    def test_fetch_reviews_success(self, mock_get_conn):
        """Test successful review fetching."""
        mock_reviews = [
            ("Movie 1", "User 1", 5, "Great!", datetime(2024, 1, 1)),
            ("Movie 2", "User 2", 4, "Good", datetime(2024, 1, 2)),
        ]

        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = mock_reviews

        mock_conn = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.__exit__.return_value = None

        mock_get_conn.return_value = mock_conn

        reviews = fetch_reviews()

        assert reviews == mock_reviews
        mock_cursor.execute.assert_called_once()

    @patch("main.get_connection")
    def test_fetch_reviews_empty(self, mock_get_conn):
        """Test fetching when no reviews exist."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []

        mock_conn = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.__exit__.return_value = None

        mock_get_conn.return_value = mock_conn

        reviews = fetch_reviews()

        assert reviews == []


class TestRenderReviewsPage:
    """Tests for HTML rendering."""

    def test_render_reviews_page_basic(self):
        """Test basic HTML rendering."""
        reviews = [
            ("Inception", "Alice", 5, "Mind-bending!", datetime(2024, 1, 1)),
        ]

        html = render_reviews_page(reviews)

        assert "<title>Movie Reviews</title>" in html
        assert "MovieMeter - Reviews" in html
        assert "Inception" in html
        assert "Alice" in html
        assert "5" in html
        assert "Mind-bending!" in html
        assert "2024-01-01" in html

    def test_render_reviews_page_xss_protection(self):
        """Test that HTML is properly escaped to prevent XSS."""
        reviews = [
            (
                "<script>alert('xss')</script>",
                "<img src=x onerror='alert(1)'>",
                5,
                "<svg onload='alert(1)'>",
                datetime(2024, 1, 1),
            ),
        ]

        html = render_reviews_page(reviews)

        # Verify that dangerous characters are escaped
        assert "&lt;script&gt;" in html
        assert "&lt;img" in html
        assert "&lt;svg" in html
        assert "<script>alert" not in html

    def test_render_reviews_page_multiple_reviews(self):
        """Test rendering multiple reviews."""
        reviews = [
            ("Movie 1", "User 1", 5, "Great", datetime(2024, 1, 1)),
            ("Movie 2", "User 2", 4, "Good", datetime(2024, 1, 2)),
            ("Movie 3", "User 3", 3, "OK", datetime(2024, 1, 3)),
        ]

        html = render_reviews_page(reviews)

        assert "Movie 1" in html
        assert "Movie 2" in html
        assert "Movie 3" in html
        assert "Read all 3 seeded ratings" in html

    def test_render_reviews_page_empty(self):
        """Test rendering with no reviews."""
        reviews = []

        html = render_reviews_page(reviews)

        assert "Read all 0 seeded ratings" in html
        assert "<tbody>" in html

    def test_render_reviews_page_date_formatting(self):
        """Test that dates are formatted correctly."""
        reviews = [
            (
                "Test Movie",
                "Test User",
                5,
                "Test",
                datetime(2024, 12, 25),
            ),
        ]

        html = render_reviews_page(reviews)

        assert "2024-12-25" in html


class TestIndexRoute:
    """Tests for Flask routes."""

    @patch("main.fetch_reviews")
    def test_index_success(self, mock_fetch, client):
        """Test successful index route."""
        mock_reviews = [
            ("Movie 1", "User 1", 5, "Great!", datetime(2024, 1, 1)),
        ]
        mock_fetch.return_value = mock_reviews

        response = client.get("/")

        assert response.status_code == 200
        assert b"Movie 1" in response.data
        assert b"MovieMeter - Reviews" in response.data

    @patch("main.fetch_reviews")
    def test_index_database_error(self, mock_fetch, client):
        """Test index route when database error occurs."""
        mock_fetch.side_effect = Exception("Database connection failed")

        response = client.get("/")

        assert response.status_code == 500
        assert b"Database error" in response.data
        assert b"Database connection failed" in response.data

    @patch("main.fetch_reviews")
    def test_index_unknown_error(self, mock_fetch, client):
        """Test index route with generic exception."""
        mock_fetch.side_effect = RuntimeError("Unexpected error")

        response = client.get("/")

        assert response.status_code == 500
        assert b"Database error" in response.data
