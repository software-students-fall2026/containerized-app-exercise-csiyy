"""Flask web application for capturing and managing photos."""

from flask import Flask, request, Response, render_template, send_from_directory
from photos import get_photo, save_photo, delete_photo

app = Flask(__name__, template_folder=".")


@app.get("/webcam")
def webcam():
    """Render the webcam capture page."""
    return render_template("capture.html")


@app.get("/<any(capture.css,capture.js):filename>")
def webcam_asset(filename):
    """Serve webcam CSS and JavaScript files."""
    return send_from_directory(app.template_folder, filename)


@app.get("/waiting")
def waiting():
    """Render the waiting page."""
    return render_template("waiting.html")


@app.get("/results")
def results():
    """Render the results page."""
    return render_template("results.html")


@app.route("/upload", methods=["POST"])
def upload():
    """Upload and save a photo to the database."""
    image = request.files.get("photo")
    if image is None:
        return {"error": "No photo uploaded"}, 400
    image_id = save_photo(image)
    if image_id is None:
        return {"error": "Empty image"}, 400
    return {"message": "Photo saved!", "image_id": image_id}, 201


@app.route("/photo/<image_id>", methods=["GET"])
def retrieve(image_id):
    """Retrieve a photo using its ID."""
    image = get_photo(image_id)
    if image is None:
        return {"error": "Photo not found"}, 404
    return Response(image["image"], mimetype=image["file_type"])


@app.route("/photo/<image_id>", methods=["DELETE"])
def remove(image_id):
    """Delete a photo using its ID."""
    deleted = delete_photo(image_id)
    if not deleted:
        return {"error": "Photo not found"}, 404
    return {
        "message": "Photo deleted successfully",
    }, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
