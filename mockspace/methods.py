import time
import json

from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask import Response
from werkzeug.exceptions import abort

from mockspace.auth import login_required
from mockspace.db import get_db
from mockspace.services import get_service_by_title

bp = Blueprint("methods", __name__)


@bp.route("/<string:service_name>", methods=("GET", "POST"))
def service(service_name):
    """Show all the methods, most recent first."""

    # redirect for unauthorized user
    if g.user is None:
        return redirect(url_for("auth.login"))

    methods = []
    db = get_db()

    service = get_service_by_title(service_name, check_author=False)

    methods = db.execute(
        "SELECT m.id, title, body, status_code, delay, supported_method, created, author_id, username"
        " FROM method m JOIN user u ON"
        " m.author_id = u.id AND"
        " m.service_id = ?"
        " ORDER BY created DESC", (service["id"],),
    ).fetchall()

    return render_template("method/services.html", methods=methods, service_name=service_name, service=service)


def get_method(service_name, method_name, check_author=True):
    """Get a method by service_name, method_name.

    Checks that the id exists and optionally that the current user is
    the author.

    :param id: id of method to get
    :param check_author: require the current user to be the author
    :return: the method with author information
    :raise 404: if a method with the given id doesn't exist
    :raise 403: if the current user isn't the author
    """

    method = (
        get_db()
            .execute(
            "SELECT m.id, m.title, m.body, m.status_code,"
            " m.delay, m.supported_method, m.headers,"
            " m.created, m.author_id, m.service_id, username"
            " FROM method m JOIN user u ON m.author_id = u.id"
            " JOIN service s ON m.service_id = s.id"
            " WHERE m.title = ? AND s.title = ?",
            (method_name, service_name),
        )
            .fetchone()
    )

    if method is None:
        abort(404, "Method {0} doesn't exist.".format(method_name))

    if check_author and method["author_id"] != g.user["id"]:
        abort(403)

    return method


def get_headers_from_request_form(request_form_data):
    """Gets form data, retrieves headers values and adds them to a tuple"""
    constant_form_fields = ['title', 'body', 'status_code', 'delay', 'supported_method']
    headers = {}

    # Python 3.7: Dictionary order is guaranteed to be insertion order. This is used to process dicts
    # The odd values of the source dictionary will become the keys of the header dictionary. Even - values.
    counter = 1
    for key, value in request_form_data.items():
        if key not in constant_form_fields:

            if counter % 2 != 0:
                headers_key = value
            else:
                headers_value = value
                headers[headers_key] = headers_value
            counter += 1

    # replacement of single by double quotes for further conversion of a string into a dictionary
    headers = str(headers).replace("'", "\"")

    return headers


@bp.route("/<string:service_name>/create_method", methods=("GET", "POST"))
@login_required
def create_method(service_name):
    """Create a new method for the current user, service."""
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        status_code = int(request.form["status_code"])
        delay = int(request.form["delay"])
        supported_method = request.form["supported_method"]
        headers = get_headers_from_request_form(request.form)
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            service_id = db.execute(
                "SELECT id FROM service WHERE title = ?", (service_name,),
            ).fetchone()

            db.execute(
                "INSERT INTO method"
                " (title, body, status_code, delay, supported_method, headers, author_id, service_id)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (title, body, status_code, delay, supported_method, headers, g.user["id"], service_id['id']),
            )
            db.commit()
            return redirect(url_for("methods.service", service_name=service_name))

    return render_template("method/create_method.html", service_name=service_name)


@bp.route("/<string:service_name>/<string:method_name>", methods=("GET", "POST", "PUT", "PATCH", "DELETE"))
def method(method_name, service_name):
    """Returns method response"""
    db = get_db()

    method = get_method(service_name, method_name, check_author=False)

    service = get_service_by_title(service_name, check_author=False)

    method_response = db.execute(
        "SELECT body, status_code, delay, supported_method, headers"
        " FROM method"
        " WHERE service_id = ? AND title = ?",
        (service["id"], method_name,),
    ).fetchone()

    body = method_response['body']
    status_code = method_response['status_code']
    delay = method_response['delay']
    supported_method = method_response['supported_method']
    headers = json.loads(method_response['headers'])

    # seconds to milliseconds
    delay = delay / 1000
    time.sleep(delay)

    if supported_method != request.method:
        return render_template("method/method_not_allowed.html", method=method, service_name=service_name,
                               method_name=method_name, current_method=request.method)

    return Response(body, status=status_code, headers=headers)


@bp.route("/<string:service_name>/<string:method_name>/update_method", methods=("GET", "POST"))
@login_required
def update_method(service_name, method_name):
    """Update a method if the current user is the author."""
    method = get_method(service_name, method_name)

    if request.method == "POST":
        title = request.form["title"].replace(' ', '_')
        body = request.form["body"]
        status_code = int(request.form["status_code"])
        delay = int(request.form["delay"])
        supported_method = request.form["supported_method"]
        headers = get_headers_from_request_form(request.form)

        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE method"
                " SET title = ?, body = ?, status_code = ?,"
                " delay = ?, supported_method = ?, headers = ?"
                " WHERE id = ?",
                (title, body, status_code, delay, supported_method, headers, method['id'])
            )
            db.commit()

            return redirect(url_for("methods.service", service_name=service_name))

    method = get_method(service_name, method_name)

    headers = json.loads(method['headers'])

    return render_template("method/update_method.html", method=method, service_name=service_name, headers=headers)


@bp.route("/<string:service_name>/<string:method_name>/delete_method", methods=("GET", "POST"))
@login_required
def delete_method(service_name, method_name):
    """Delete the method.

    Ensures that the method exists and that the logged in user is the
    author of the method.
    """
    method_for_delete = get_method(service_name, method_name)
    db = get_db()
    db.execute("DELETE FROM method"
               " WHERE title = ? AND service_id = ?", (method_name, method_for_delete['service_id']))
    db.commit()

    return redirect(url_for("methods.service", service_name=service_name))
