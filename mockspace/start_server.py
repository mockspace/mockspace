import os


def start_server():
    """Tells Waitress to start the server"""

    start_command = 'waitress-serve --call "mockspace:create_app"'
    os.system(start_command)
