# API - Orthomosaic Rotation

This directory contains code for the rotation of orthomosaics, a crucial process in the image processing of aerial or satellite images. The purpose is to align images with the horizontal axis. The code provides functionalities for image loading, processing, and rotation correction.

## FastAPI Image Processing Service

This FastAPI application is designed to provide image processing capabilities, including rotation and background removal, for image files. It offers the following endpoints:

- `GET /token-auth`: This endpoint is used to obtain an authentication token by sending a username and password to an external authentication service. The token is required for accessing protected routes.

- `GET /get-orthophoto`: This endpoint fetches an orthophoto image file from an external service, processes it, and returns the processed image along with its rotation angle. It requires a project ID, task ID, and a valid authentication token.

- `POST /upload`: This endpoint allows users to upload an image file for processing. The uploaded image is processed to remove the background and return the processed image along with its rotation angle.

- `GET /download/{filename}`: This endpoint allows users to download previously processed image files from the server.

## Requirements

Before running the application, ensure that you have the following requirements installed:

    Python 3.x
    FastAPI
    OpenCV (cv2)
    NumPy
    scikit-image (skimage)
    Pillow (PIL)
    Requests
    uvicorn

You can install these dependencies using pip with the following command:

```
$pip install fastapi opencv-python-headless numpy scikit-image pillow requests uvicorn.

```
## Usage

1. Clone this repository or download the code.
2. Start the FastAPI application by running the following command:

```
$uvicorn main:app --host 0.0.0.0 --port 8001

```

This will start the application on http://localhost:8001.

1.Use the provided endpoints to interact with the service:

    - Access the API documentation and test the endpoints by navigating to http://localhost:8001/docs.
    - Obtain an authentication token using the /token-auth endpoint.
    - Fetch and process orthophoto images using the /get-orthophoto endpoint.
    - Upload images for processing using the /upload endpoint.
    - Download processed images using the /download/{filename} endpoint.
