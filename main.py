from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import os
from io import BytesIO
from PIL import Image
import cv2
import numpy as np
from skimage.color import rgb2gray
from skimage.filters import threshold_otsu
from skimage.feature import canny
from skimage.transform import probabilistic_hough_line
from skimage import io
import requests

app = FastAPI()

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def processed_image(file_path):
    # Load the image
    imageOriginal = cv2.imread(file_path)

    # Binarize the image
    image = rgb2gray(imageOriginal[:, :, :3])  # Remove the alpha channel
    threshold = threshold_otsu(image)
    binary_image = image < threshold

    # Find edges
    edges = canny(binary_image)

    # Find the rotation angle
    lines = probabilistic_hough_line(edges, threshold=100, line_length=80, line_gap=5)
    angles = []
    for line in lines:
        p0, p1 = line
        dx = p1[0] - p0[0]
        dy = p1[1] - p0[1]
        angle = np.arctan2(dy, dx) * 180 / np.pi
        angles.append(angle)
    angle = np.mean(angles)
    if angle < 0:
        r_angle = angle + 90
    else:
        r_angle = angle - 90

    # Rotate the image
    rows, cols = imageOriginal.shape[:2]

    M = cv2.getRotationMatrix2D((cols // 2, rows // 2), r_angle, 1)

   # Calculate the new image dimensions
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])

    new_cols = int((rows * sin) + (cols * cos))
    new_rows = int((rows * cos) + (cols * sin))

    # Adjust the rotation matrix to take into account translation
    M[0, 2] += (new_cols / 2) - cols // 2
    M[1, 2] += (new_rows / 2) - rows // 2

    # Rotate the image
    rotated_image = cv2.warpAffine(imageOriginal, M, (new_cols, new_rows))
    rotated_image_png = cv2.warpAffine(imageOriginal, M, (new_cols, new_rows))
    # Substitute the black background with a transparent background
    rotated_image_png[np.all(rotated_image_png == [0, 0, 0], axis=-1)] = [255, 255, 255]

    # Save the image in upload directory
    output_file_path = os.path.abspath(os.path.join(UPLOAD_DIR, "rotated_image.png"))
    cv2.imwrite(output_file_path, rotated_image_png)

    # Convert the image to bytes
    img_byte_arr = cv2.imencode(".tif", rotated_image)[1].tobytes()

    # Substitue the black background with a transparent background
    img = Image.open(BytesIO(img_byte_arr))
    img = img.convert("RGBA")
    datas = img.getdata()

    newData = []
    for item in datas:
        if item[0] == 0 and item[1] == 0 and item[2] == 0:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)

    img.putdata(newData)

    # Convert the image to bytes
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format="TIFF")
    img_byte_arr = img_byte_arr.getvalue()

    # Save the resulting image to tif
    output_file_path = os.path.abspath(os.path.join(UPLOAD_DIR, "output.tif"))
    with open(output_file_path, 'wb') as f:
        f.write(img_byte_arr)

    return output_file_path, r_angle

@app.get("/token-auth")
async def token_auth(username: str, password: str):
    # Get the authentication token
    res = requests.post('http://localhost:8000/api/token-auth/', 
                        data={'username': username,
                              'password': password}).json()
    token = res['token']
    return {"token": token}

@app.get("/get-orthophoto")
async def get_orthophoto(project_id: str, task_id: str, token: str):
    res = requests.get("http://localhost:8000/api/projects/{}/tasks/{}/download/orthophoto.tif".format(project_id, task_id), 
                        headers={'Authorization': 'JWT {}'.format(token)},
                        stream=True)
    
    orthophoto_file_name = "orthophoto.tif"  
    orthophoto_path = os.path.abspath(orthophoto_file_name)  

    with open("orthophoto.tif", 'wb') as f:
        for chunk in res.iter_content(chunk_size=1024): 
            if chunk:
                f.write(chunk)
    output_file_path = processed_image(orthophoto_path)
    return FileResponse(output_file_path, media_type="image/tif", filename="output.tif")
    
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Save the uploaded file
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())
    
    # Process the image
    output_file_path, r_angle = processed_image(file_path)
    
    return (FileResponse(output_file_path, media_type="image/tif"), r_angle)

@app.get("/download/{filename}")
async def download_image(filename: str):
    file_path = os.path.abspath(os.path.join(UPLOAD_DIR, filename))
    if os.path.isfile(file_path):
        return FileResponse(file_path, media_type="image/tif", filename=filename)
    else:
        return {"message": "File not found"}
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
