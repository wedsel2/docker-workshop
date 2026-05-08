"""Unit tests for verify_seed_data.py"""

from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest

from verify_seed_data import count_seed_rows


class TestCountSeedRows:
    """Tests for seed row counting function."""

    def test_count_seed_rows_valid(self):
        """Test counting valid seed rows."""
        sql_content = """
        INSERT INTO reviews (movie_title, reviewer, rating, review_text, created_at) VALUES
        ('Movie 1', 'Reviewer 1', 5, 'Great!', '2024-01-01'),
        ('Movie 2', 'Reviewer 2', 4, 'Good!', '2024-01-02'),
        ('Movie 3', 'Reviewer 3', 3, 'OK', '2024-01-03');
        """

        with NamedTemporaryFile(mode="w", suffix=".sql", delete=False) as f:
            f.write(sql_content)
            f.flush()
            sql_path = Path(f.name)

        try:
            count = count_seed_rows(sql_path)
            assert count == 3
        finally:
            sql_path.unlink()

    def test_count_seed_rows_single_row(self):
        """Test counting a single seed row."""
        sql_content = """
        INSERT INTO reviews (movie_title, reviewer, rating, review_text, created_at) VALUES
        ('Movie 1', 'Reviewer 1', 5, 'Great!', '2024-01-01');
        """

        with NamedTemporaryFile(mode="w", suffix=".sql", delete=False) as f:
            f.write(sql_content)
            f.flush()
            sql_path = Path(f.name)

        try:
            count = count_seed_rows(sql_path)
            assert count == 1
        finally:
            sql_path.unlink()

    def test_count_seed_rows_multiline_values(self):
        """Test counting rows with values on multiple lines."""
        sql_content = """
        INSERT INTO reviews (movie_title, reviewer, rating, review_text, created_at) VALUES
        (
            'Movie 1', 'Reviewer 1', 5, 'Great!', '2024-01-01'
        ),
        (
            'Movie 2', 'Reviewer 2', 4, 'Good!', '2024-01-02'
        );
        """

        with NamedTemporaryFile(mode="w", suffix=".sql", delete=False) as f:
            f.write(sql_content)
            f.flush()
            sql_path = Path(f.name)

        try:
            count = count_seed_rows(sql_path)
            assert count == 2
        finally:
            sql_path.unlink()

    def test_count_seed_rows_no_insert(self):
        """Test counting when no INSERT statement exists."""
        sql_content = """
        CREATE TABLE reviews (
            id SERIAL PRIMARY KEY,
            movie_title VARCHAR(255),
            reviewer VARCHAR(255)
        );
        """

        with NamedTemporaryFile(mode="w", suffix=".sql", delete=False) as f:
            f.write(sql_content)
            f.flush()
            sql_path = Path(f.name)

        try:
            count = count_seed_rows(sql_path)
            assert count == 0
        finally:
            sql_path.unlink()

    def test_count_seed_rows_different_insert(self):
        """Test that it only counts INSERT INTO reviews rows."""
        sql_content = """
        INSERT INTO other_table VALUES (1), (2);
        INSERT INTO reviews (movie_title, reviewer, rating, review_text, created_at) VALUES
        ('Movie 1', 'Reviewer 1', 5, 'Great!', '2024-01-01'),
        ('Movie 2', 'Reviewer 2', 4, 'Good!', '2024-01-02');
        """

        with NamedTemporaryFile(mode="w", suffix=".sql", delete=False) as f:
            f.write(sql_content)
            f.flush()
            sql_path = Path(f.name)

        try:
            count = count_seed_rows(sql_path)
            assert count == 2
        finally:
            sql_path.unlink()

    def test_count_seed_rows_whitespace_handling(self):
        """Test that leading/trailing whitespace is handled correctly."""
        sql_content = """
        INSERT INTO reviews (movie_title, reviewer, rating, review_text, created_at) VALUES
            ( 'Movie 1', 'Reviewer 1', 5, 'Great!', '2024-01-01' )  ,
            (   'Movie 2', 'Reviewer 2', 4, 'Good!', '2024-01-02'   )
            ;
        """

        with NamedTemporaryFile(mode="w", suffix=".sql", delete=False) as f:
            f.write(sql_content)
            f.flush()
            sql_path = Path(f.name)

        try:
            count = count_seed_rows(sql_path)
            assert count == 2
        finally:
            sql_path.unlink()
