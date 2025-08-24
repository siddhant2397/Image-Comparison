import streamlit as st
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
import io

# Azure Computer Vision credentials
endpoint = st.secrets["azure_endpoint"]
key = st.secrets["azure_key"]

# Initialize client
client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(key))

st.title("Image Difference Detection using Azure Computer Vision")

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

if uploaded_file1 and uploaded_file2:
    image1 = io.BytesIO(uploaded_file1.read())
    image2 = io.BytesIO(uploaded_file2.read())

    analysis1 = analyze_image(image1)
    analysis2 = analyze_image(image2)

    tags1, objects1 = get_tags_and_objects(analysis1)
    tags2, objects2 = get_tags_and_objects(analysis2)

    st.write("Tags in image 1:", tags1)
    st.write("Tags in image 2:", tags2)

    st.write("Objects in image 1:", objects1)
    st.write("Objects in image 2:", objects2)

    diff_tags = tags1.symmetric_difference(tags2)
    diff_objects = objects1.symmetric_difference(objects2)

    st.write("Different tags between images:", diff_tags)
    st.write("Different objects between images:", diff_objects)

else:
    st.write("Please upload two images to compare.")
