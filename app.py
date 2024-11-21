import cv2
import streamlit as st
import numpy as np
from pyzbar.pyzbar import decode

def get_available_cameras(max_devices=5):
    available_cameras = []
    for index in range(max_devices):
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            available_cameras.append(index)
            cap.release()
    return available_cameras


def main():
    st.title("Simple WebRTC Stream with OpenCV and Streamlit")

    available_cameras = get_available_cameras()
    if not available_cameras:
        st.error("No camera devices found.")
        return

    camera_index = st.selectbox('Select Camera', available_cameras)
    run = st.checkbox('Run Webcam', key='run_webcam')
    FRAME_WINDOW = st.image([])
    barcode_text = st.empty()

    if run:
        # Initialize the video capture object
        cap = cv2.VideoCapture(camera_index)

        while run:
            # Capture each frame of the video
            ret, frame = cap.read()
            if not ret:
                st.error(f"Failed to capture image from camera {camera_index}.")
                break

            # Decode barcodes
            barcodes = decode(frame)
            for barcode in barcodes:
                (x, y, w, h) = barcode.rect
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                barcode_data = barcode.data.decode("utf-8")
                barcode_type = barcode.type
                text = f"{barcode_data} ({barcode_type})"
                cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                barcode_text.write(f"Detected Barcode: {text}")

            # Convert the image color from BGR to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Displaying the frame using Streamlit
            FRAME_WINDOW.image(frame)

        # Release the video capture object
        cap.release()


if __name__ == "__main__":
    main()
