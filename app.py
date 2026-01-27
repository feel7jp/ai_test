from flask import Flask, send_from_directory
import os
import sys

from routes import routes
from settings import port

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_STATIC_DIR = os.path.join(BASE_DIR, "public", "static")

app = Flask(__name__, static_folder=None)
app.register_blueprint(routes)


@app.get("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(PUBLIC_STATIC_DIR, filename)


if __name__ == "__main__":
    # Check if --debug flag is passed
    debug = "--debug" in sys.argv or "-d" in sys.argv
    app.run(debug=debug, port=port())
