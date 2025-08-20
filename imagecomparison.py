import streamlit as st
import cv2
import numpy as np
from PIL import Image

st.title("AKAZE Image Feature Comparison")

img1 = st.file_uploader("Upload First Image", type=['jpg', 'png', 'jpeg'])
img2 = st.file_uploader("Upload Second Image", type=['jpg', 'png', 'jpeg'])
def draw_keypoints(image, kp, color=(0, 0, 255)):
    # Draw circles for keypoints (change)
    return cv2.drawKeypoints(image, kp, None, color, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)


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
            #good_matches = []
            good_matches_idx1 = set()
            good_matches_idx2 = set()
            for i, (m, n) in enumerate(matches):
                if m.distance < 0.7 * n.distance:
                    #good_matches.append(m)
                    good_matches_idx1.add(m.queryIdx)
                    good_matches_idx2.add(m.trainIdx)
            #match_img = cv2.drawMatches(image1, kp1, image2, kp2, good_matches, None, flags=2)
            #match_img_rgb = cv2.cvtColor(match_img, cv2.COLOR_BGR2RGB)
            #st.image(match_img_rgb, caption="AKAZE Feature Matches")
            unmatched_kp1 = [kp for i, kp in enumerate(kp1) if i not in good_matches_idx1]
            unmatched_kp2 = [kp for i, kp in enumerate(kp2) if i not in good_matches_idx2]
            # Draw only unmatched keypoints (differences)
            diff_img1 = draw_keypoints(image1, unmatched_kp1)
            diff_img2 = draw_keypoints(image2, unmatched_kp2)
            st.write("Unmatched keypoints (differences) are highlighted in each image below:")
            st.image(cv2.cvtColor(diff_img1, cv2.COLOR_BGR2RGB), caption="Differences in First Image")
            st.image(cv2.cvtColor(diff_img2, cv2.COLOR_BGR2RGB), caption="Differences in Second Image")
    except Exception as e:
        st.error(f"Error processing images: {e}")
