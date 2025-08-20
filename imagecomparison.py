import streamlit as st
import cv2
import numpy as np
from PIL import Image

st.title("AKAZE Image Feature Comparison")

img1 = st.file_uploader("Upload First Image", type=['jpg', 'png', 'jpeg'])
img2 = st.file_uploader("Upload Second Image", type=['jpg', 'png', 'jpeg'])

if img1 and img2:
    try:
        image1 = np.array(Image.open(img1).convert('RGB'))
        image2 = np.array(Image.open(img2).convert('RGB'))
        image1_gray = cv2.cvtColor(image1, cv2.COLOR_RGB2GRAY)
        image2_gray = cv2.cvtColor(image2, cv2.COLOR_RGB2GRAY)
        akaze = cv2.AKAZE_create()
        kp1, des1 = akaze.detectAndCompute(image1_gray, None)
        kp2, des2 = akaze.detectAndCompute(image2_gray, None)
        if des1 is None or des2 is None:
            st.warning("No features found in one or both images. Please use clearer images.")
        else:
            bf = cv2.BFMatcher(cv2.NORM_HAMMING)
            matches = bf.knnMatch(des1, des2, k=2)
            good_matches = []
            for m, n in matches:
                if m.distance < 0.7 * n.distance:
                    good_matches.append(m)
            match_img = cv2.drawMatches(image1, kp1, image2, kp2, good_matches, None, flags=2)
            match_img_rgb = cv2.cvtColor(match_img, cv2.COLOR_BGR2RGB)
            st.image(match_img_rgb, caption="AKAZE Feature Matches")
    except Exception as e:
        st.error(f"Error processing images: {e}")
