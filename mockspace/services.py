from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort

from mockspace.auth import login_required
from mockspace.db import get_db

bp = Blueprint("services", __name__)


@bp.route("/")
def index():
    """Show all the services, most recent first."""

    # redirect for unauthorized user
    if g.user is None:
        return redirect(url_for("auth.login"))

    db = get_db()
    services = db.execute(
        "SELECT s.id, title, body, created, author_id, username"
        " FROM service s JOIN user u ON s.author_id = u.id"
        " ORDER BY created DESC"
    ).fetchall()

    return render_template("service/index.html", services=services)


def get_service_by_title(title, check_author=True):
    """Get a service by title.

    Checks that the id exists and optionally that the current user is
    the author.

    :param id: id of service to get
    :param check_author: require the current user to be the author
    :return: the service with author information
    :raise 404: if a service with the given id doesn't exist
    :raise 403: if the current user isn't the author
    """
    service = (
        get_db()
            .execute(
            "SELECT s.id, s.title, s.body, s.created, s.author_id, username"
            " FROM service s JOIN user u ON s.author_id = u.id"
            " WHERE s.title = ?",
            (title,),
        )
            .fetchone()
    )

    if service is None:
        abort(404, "Service '{0}' doesn't exist.".format(title))

    if check_author and service["author_id"] != g.user["id"]:
        abort(403)

    return service


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    """Create a new service for the current user."""
    if request.method == "POST":
        title = request.form["title"].replace(' ', '_')
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO service (title, body, author_id) VALUES (?, ?, ?)",
                (title, body, g.user["id"]),
            )
            db.commit()
            return redirect(url_for("services.index"))

    return render_template("service/create.html")


@bp.route("/<string:service_name>/update", methods=("GET", "POST"))
@login_required
def update(service_name):
    """Update a service if the current user is the author."""
    service = get_service_by_title(service_name)

    if request.method == "POST":
        title = request.form["title"].replace(' ', '_')
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE service SET title = ?, body = ? WHERE id = ?", (title, body, service["id"])
            )
            db.commit()
            return redirect(url_for("services.index"))

    return render_template("service/update.html", service=service)


@bp.route("/<string:service_name>/delete", methods=("GET", "POST"))
@login_required
def delete(service_name):
    """Delete a service.

    Ensures that the service exists and that the logged in user is the
    author of the service.
    """
    get_service_by_title(service_name)
    db = get_db()
    db.execute("DELETE FROM service WHERE title = ?", (service_name,))
    db.commit()
    return redirect(url_for("services.index"))
