import cv2
import streamlit as st
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
    st.title("Barcode Scanner with OpenCV and Streamlit")
    available_cameras = get_available_cameras()
    if not available_cameras:
        st.error("No camera devices found.")
        return
    camera_index = st.selectbox('Select Camera', available_cameras)
    run = st.checkbox('Run Webcam', key='run_webcam')
    FRAME_WINDOW = st.image([])
    barcode_text = st.empty()
    if run:
        cap = cv2.VideoCapture(camera_index)
        while run:
            ret, frame = cap.read()
            if not ret:
                st.error(f"Failed to capture image from camera {camera_index}.")
                break
            # Convert to grayscale for better barcode detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Decode barcodes
            barcodes = decode(gray)
            for barcode in barcodes:
                (x, y, w, h) = barcode.rect
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                barcode_data = barcode.data.decode("utf-8")
                barcode_type = barcode.type
                text = f"{barcode_data} ({barcode_type})"
                cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                barcode_text.write(f"Detected Barcode: {text}")
            # Convert to RGB for Streamlit display
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            FRAME_WINDOW.image(frame)
            # Allow Streamlit checkbox to exit loop
            if not st.session_state.run_webcam:
                break
        cap.release()


if __name__ == "__main__":
    main()
