from flask import Flask, request, jsonify, Response, render_template
from photos import (get_photo, save_photo, delete_photo)
app = Flask(
    __name__, 
    template_folder='../webapp'
)

@app.get("/webcam")
def webcam():
    return render_template("webcam.html")

@app.get("/waiting")
def waiting():
    return render_template("waiting.html")

@app.get("/results")
def results():
    return render_template("results.html")

@app.route('/upload', methods = ['POST'])
def upload():
    image = request.files.get('photo')
    if image is None:
        return {"error": "No photo uploaded"}, 400
    image_id = save_photo(image)
    if image_id is None:
        return {"error": "Empty image"}, 400
    return{
        "message":"Photo saved!",
        "image_id":image_id
    }, 201

@app.route('/photo/<image_id>', methods = ['GET'])
def retrieve(image_id):
    image = get_photo(image_id)
    if image is None:
        return {"error": "Photo not found"}, 404
    return Response(
        image['image'],
        mimetype=image['file_type']
    )

@app.route('/photo/<image_id>', methods = ['DELETE'])
def remove(image_id):
    deleted = delete_photo(image_id)
    if not deleted:
        return {"error": "Photo not found"}, 404
    return{
        "message":"Photo deleted successfully",
    }, 200

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)