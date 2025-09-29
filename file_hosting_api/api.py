import os

from flask import Flask, request, abort, jsonify, send_from_directory


UPLOAD_DIRECTORY = os.path.join(os.path.dirname(__file__), "api_hosted_files")

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)


api = Flask(__name__)


@api.route("/files")
def list_files():
    """List all stored files."""
    files = []
    for filename in os.listdir(UPLOAD_DIRECTORY):
        path = os.path.join(UPLOAD_DIRECTORY, filename)
        if os.path.isfile(path):
            files.append(filename)
    return jsonify(files)


@api.route("/files/<path:path>")
def get_file(path):
    """Download a stored file."""
    return send_from_directory(UPLOAD_DIRECTORY, path, as_attachment=True)


@api.route("/files/<filename>", methods=["POST"])
def post_file(filename):
    """Upload a new file."""

    if "/" in filename:
        abort(400, "No subdirectories allowed")

    with open(os.path.join(UPLOAD_DIRECTORY, filename), "wb") as fp:
        fp.write(request.data)

    return "", 200

@api.route("/files/<filename>", methods=["DELETE"])
def delete_file(filename):
    """Delete a stored file."""

    if "/" in filename:
        abort(400, "no subdirectories allowed")

    file_path = os.path.join(UPLOAD_DIRECTORY, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return {"message": f"{filename} deleted"}, 200
    else:
        abort(404, f"File {filename} not found")

if __name__ == "__main__":
    api.run(debug=True, port=8000)
