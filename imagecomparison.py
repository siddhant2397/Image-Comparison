import streamlit as st
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
import cv2
import numpy as np
from PIL import Image
import io

# Retrieve Azure credentials from Streamlit secrets
endpoint = st.secrets["azure_endpoint"]
key = st.secrets["azure_key"]

# Initialize Azure Computer Vision client
client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(key))

st.title("Image Difference Detection with Azure Vision & Visual Diff")

uploaded_file1 = st.file_uploader("Upload first image", type=["jpg", "jpeg", "png"])
uploaded_file2 = st.file_uploader("Upload second image", type=["jpg", "jpeg", "png"])

def analyze_image(image_stream):
    return client.analyze_image_in_stream(
        image_stream,
        visual_features=[VisualFeatureTypes.tags, VisualFeatureTypes.objects]
    )

def get_tags_and_objects(analysis):
    tags = set([tag.name for tag in analysis.tags])
    objects = set([obj.object_property for obj in analysis.objects])
    return tags, objects

def convert_to_cv2(image_bytes):
    # Convert bytes to OpenCV image (numpy array, BGR format)
    pil_image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    cv_image = np.array(pil_image)
    return cv2.cvtColor(cv_image, cv2.COLOR_RGB2BGR)

def compute_image_diff(img1_bgr, img2_bgr):
    # Resize images if necessary for size equality
    if img1_bgr.shape != img2_bgr.shape:
        img2_bgr = cv2.resize(img2_bgr, (img1_bgr.shape[1], img1_bgr.shape[0]))

    # Compute absolute difference between images
    diff = cv2.absdiff(img1_bgr, img2_bgr)

    # Convert to grayscale
    gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

    # Threshold the difference image to get areas of significant change
    _, thresh = cv2.threshold(gray_diff, 30, 255, cv2.THRESH_BINARY)

    # Dilate the thresholded image to enlarge differences
    kernel = np.ones((5,5), np.uint8)
    dilated = cv2.dilate(thresh, kernel, iterations=2)

    # Create a red mask for difference areas
    mask = np.zeros_like(img1_bgr)
    mask[:, :, 2] = dilated  # Red channel

    # Overlay red mask on original image to highlight differences
    highlighted = cv2.addWeighted(img1_bgr, 1, mask, 0.5, 0)

    return highlighted, dilated

def draw_diff_contours(original_img, diff_mask):
    contours, _ = cv2.findContours(diff_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contour_img = original_img.copy()
    cv2.drawContours(contour_img, contours, -1, (0, 255, 0), 3)  # Green contours
    return contour_img


if uploaded_file1 and uploaded_file2:
    # Read raw bytes for OpenCV
    img_bytes1 = uploaded_file1.read()
    img_bytes2 = uploaded_file2.read()

    # Analyze images with Azure Computer Vision
    analysis1 = analyze_image(io.BytesIO(img_bytes1))
    analysis2 = analyze_image(io.BytesIO(img_bytes2))

    tags1, objects1 = get_tags_and_objects(analysis1)
    tags2, objects2 = get_tags_and_objects(analysis2)

    st.subheader("Azure Computer Vision Analysis")
    diff_tags = tags1.symmetric_difference(tags2)
    diff_objects = objects1.symmetric_difference(objects2)

    st.write("Different tags between images:", diff_tags)
    st.write("Different objects between images:", diff_objects)

    # Convert to OpenCV format
    cv_img1 = convert_to_cv2(img_bytes1)
    cv_img2 = convert_to_cv2(img_bytes2)

    # Compute visual difference with highlighting
    highlighted_diff, diff_mask = compute_image_diff(cv_img1, cv_img2)
    contour_highlighted = draw_diff_contours(cv_img1, diff_mask)

    st.subheader("Visual Difference Highlight with Contours")
    st.image(cv2.cvtColor(contour_highlighted, cv2.COLOR_BGR2RGB), use_column_width=True)
    
else:
    st.write("Please upload two images to compare.")
