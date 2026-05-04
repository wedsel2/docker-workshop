import html
import os
import time

import psycopg2
from flask import Flask

app = Flask(__name__)


def get_connection(max_attempts: int = 20, delay_seconds: int = 2):
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = int(os.getenv("DB_PORT", "5432"))
    db_name = os.getenv("DB_NAME", "moviereviews")
    db_user = os.getenv("DB_USER", "appuser")
    db_password = os.getenv("DB_PASSWORD", "apppass")

    for attempt in range(1, max_attempts + 1):
        try:
            return psycopg2.connect(
                host=db_host,
                port=db_port,
                dbname=db_name,
                user=db_user,
                password=db_password,
            )
        except psycopg2.OperationalError:
            if attempt == max_attempts:
                raise
            time.sleep(delay_seconds)


def fetch_reviews():
    query = """
        SELECT movie_title, reviewer, rating, review_text, created_at
        FROM reviews
        ORDER BY id
    """

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()


def render_reviews_page(reviews):
    rows = []
    for movie_title, reviewer, rating, review_text, created_at in reviews:
        rows.append(
            "<tr>"
            f"<td class='movie-cell'>{html.escape(movie_title)}</td>"
            f"<td>{html.escape(reviewer)}</td>"
            f"<td><span class='rating-pill'>{rating}</span></td>"
            f"<td class='review-cell'>{html.escape(review_text)}</td>"
            f"<td>{created_at.strftime('%Y-%m-%d')}</td>"
            "</tr>"
        )

    table_rows = "\n".join(rows)

    return f"""
    <html>
        <head>
            <meta charset='utf-8'>
            <meta name='viewport' content='width=device-width, initial-scale=1'>
            <title>Movie Reviews</title>
            <style>
                :root {{
                    --bg: #eceff4;
                    --surface: #ffffff;
                    --surface-alt: #f7f8fb;
                    --text-main: #1f2937;
                    --text-soft: #5b6473;
                    --border: #dfe4ee;
                    --header: #111317;
                    --accent: #f5c518;
                }}

                * {{ box-sizing: border-box; }}

                body {{
                    margin: 0;
                    font-family: Inter, Segoe UI, Roboto, Arial, sans-serif;
                    background: linear-gradient(180deg, #f0f3f8 0%, var(--bg) 100%);
                    color: var(--text-main);
                }}

                .topbar {{
                    background: var(--header);
                    color: #ffffff;
                    border-bottom: 3px solid var(--accent);
                    padding: 1rem 1.5rem;
                }}

                .brand {{
                    margin: 0;
                    font-size: 1.1rem;
                    font-weight: 700;
                    letter-spacing: 0.02em;
                }}

                .container {{
                    max-width: 1080px;
                    margin: 1.5rem auto 2rem;
                    padding: 0 1rem;
                }}

                .panel {{
                    background: var(--surface);
                    border: 1px solid var(--border);
                    border-radius: 14px;
                    box-shadow: 0 10px 28px rgba(14, 23, 38, 0.08);
                    overflow: hidden;
                }}

                .panel-header {{
                    padding: 1.2rem 1.3rem;
                    border-bottom: 1px solid var(--border);
                    background: var(--surface-alt);
                }}

                .panel-title {{
                    margin: 0;
                    font-size: 1.3rem;
                }}

                .panel-subtitle {{
                    margin: 0.4rem 0 0;
                    color: var(--text-soft);
                    font-size: 0.95rem;
                }}

                .table-wrap {{
                    overflow-x: auto;
                }}

                table {{
                    width: 100%;
                    border-collapse: collapse;
                    min-width: 760px;
                }}

                th, td {{
                    padding: 0.85rem 1rem;
                    text-align: left;
                    vertical-align: top;
                    border-bottom: 1px solid var(--border);
                }}

                th {{
                    background: #f1f4f8;
                    color: #374151;
                    text-transform: uppercase;
                    font-size: 0.73rem;
                    letter-spacing: 0.08em;
                    font-weight: 700;
                }}

                tbody tr:hover {{
                    background: #fafbfd;
                }}

                .movie-cell {{
                    font-weight: 700;
                }}

                .review-cell {{
                    color: #2f3a4d;
                    line-height: 1.45;
                }}

                .rating-pill {{
                    display: inline-block;
                    min-width: 3rem;
                    text-align: center;
                    background: var(--accent);
                    color: #111;
                    font-weight: 700;
                    border-radius: 999px;
                    padding: 0.2rem 0.55rem;
                }}

                @media (max-width: 700px) {{
                    .brand {{ font-size: 1rem; }}
                    .panel-title {{ font-size: 1.1rem; }}
                    th, td {{ padding: 0.7rem 0.8rem; }}
                }}
            </style>
        </head>
        <body>
            <header class='topbar'>
                <p class='brand'>MovieMeter - Reviews</p>
            </header>

            <main class='container'>
                <section class='panel'>
                    <div class='panel-header'>
                        <h1 class='panel-title'>Top Movie Reviews</h1>
                        <p class='panel-subtitle'>Read all {len(reviews)} seeded ratings and opinions from our demo database.</p>
                    </div>

                    <div class='table-wrap'>
                        <table>
                            <thead>
                                <tr>
                                    <th>Movie</th>
                                    <th>Reviewer</th>
                                    <th>Rating</th>
                                    <th>Review</th>
                                    <th>Date</th>
                                </tr>
                            </thead>
                            <tbody>
                                {table_rows}
                            </tbody>
                        </table>
                    </div>
                </section>
            </main>
        </body>
    </html>
    """


@app.route("/")
def index():
    try:
        reviews = fetch_reviews()
        return render_reviews_page(reviews)
    except Exception as exc:
        return f"Database error: {html.escape(str(exc))}", 500


if __name__ == "__main__":
    port = int(os.getenv("APP_PORT", "8000"))
    app.run(host="0.0.0.0", port=port)
