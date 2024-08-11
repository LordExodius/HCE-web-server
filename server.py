import numpy as np
import os
import requests
import json
import io
from PIL import Image
from dotenv import load_dotenv
from collections import defaultdict
from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
# import timeit

# Initialize labels and session so no reconnection delay
load_dotenv()
labelMap = defaultdict(str)
session = requests.Session()

app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if os.getenv("DOCKER_SHARED_IP"):
    baseUrl = "http://" + os.getenv("DOCKER_SHARED_IP")
else:
    baseUrl = os.getenv("TF_SERVING_ADDR")
    
tfServingUrl = f"{baseUrl}/v1/models/{os.getenv('MODEL_NAME')}:predict"

print("tf-serving:", tfServingUrl)

def to_numpy(im: Image.Image):
    """
    Source : Fast import of Pillow images to NumPy / OpenCV arrays Written by Alex Karpinsky
    https://uploadcare.com/blog/fast-import-of-pillow-images-to-numpy-opencv-arrays/
    """
    im.load()

    # Unpack data
    e = Image._getencoder(im.mode, "raw", im.mode)
    e.setimage(im.im)

    # NumPy buffer for the result
    shape, typestr = Image._conv_type_shape(im)
    data = np.empty(shape, dtype=np.dtype(typestr))
    mem = data.data.cast("B", (data.data.nbytes,))

    bufsize, s, offset = 65536, 0, 0
    while not s:
        l, s, d = e.encode(bufsize)

        mem[offset:offset + len(d)] = d
        offset += len(d)
    if s < 0:
        raise RuntimeError("encoder error %d in tobytes" % s)
    return data

# Load labels into map
def load_labels(path: str):
    with open(path) as file:
        for line in file:
            classNum, className = line.split(" ", 1)
            labelMap[int(classNum)] = className.strip()

# Preprocess image into shape (1, h, w, 3)
def preprocess_image(imageFile):
    img = Image.open(io.BytesIO(imageFile))
    imgWidth, imgHeight = img.size
    npImg = to_numpy(img).reshape((imgHeight, imgWidth, 3)).astype(np.uint8)
    expandedNpImg = np.expand_dims(npImg, axis=0).astype(np.uint8)
    return expandedNpImg

# Parse tf-serving api output
def parse_response(res, threshold):
    predictions = json.loads(res)["predictions"][0]
    boxes = predictions["detection_boxes"]
    classes = predictions["detection_classes"]
    scores = predictions["detection_scores"]

    # Array of objects with scores above threshold
    objs = [{
            "className": labelMap[classes[i]],
            "score": scores[i],
            "y1": boxes[i][0],
            "x1": boxes[i][1],
            "y2": boxes[i][2],
            "x2": boxes[i][3]
        } for i in range(len(classes)) if scores[i] > threshold]
    return objs

def packageObjects(res, threshold):
    objs = parse_response(res, threshold) 
    response = {
        "numObjects": len(objs),
        "threshold": threshold,
        "objects": objs
    }
    return response

@app.get("/")
def index():
    return {"Webserver for tf-serving"}

@app.post("/image")
async def parseImage(image: UploadFile):
    try:
        imgFile = await image.read()
        payload = { "instances": preprocess_image(imgFile).tolist() }
        res = session.post(tfServingUrl, data=json.dumps(payload))
        threshold = 0.5
        response = packageObjects(res.text, threshold)
        print(response)
        return response

    except Exception as e:
        print("POST /image error:", e)
        return e

# TODO: Video route

labelPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "res", "labels.txt")
load_labels(labelPath)

def testEndpoint():
    testImage = "./dog_bike_car.jpg"
    payload = { "instances": preprocess_image(testImage).tolist() }
    res = session.post(tfServingUrl, data=json.dumps(payload))
    return packageObjects(res.text, 0.5)