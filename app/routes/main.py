from flask import Blueprint, render_template

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    """Render the landing page."""
    return render_template("home.html")


@main_bp.route("/analyze")
def analyzer():
    """Render the sentiment analyzer page."""
    return render_template("analyzer.html")


@main_bp.route("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}, 200
