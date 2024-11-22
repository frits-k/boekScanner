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


def crop_center(frame, crop_width, crop_height):
    height, width, _ = frame.shape
    x_start = (width - crop_width) // 2
    y_start = (height - crop_height) // 2
    x_end = x_start + crop_width
    y_end = y_start + crop_height
    return frame[y_start:y_end, x_start:x_end]


def detect_barcode(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    barcodes = decode(gray)
    for barcode in barcodes:
        (x, y, w, h) = barcode.rect
        barcode_data = barcode.data.decode("utf-8")
        if barcode_data.startswith("978") or barcode_data.startswith("979"):
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            barcode_type = barcode.type
            text = f"{barcode_data} ({barcode_type})"
            cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            barcode_text.write(f"Detected Barcode: {text}")
    return frame


# Initialize session state variables
if "camera_index" not in st.session_state:
    st.session_state.camera_index = 0

pages = st.sidebar.radio("Navigation", ["Main", "Options"])

if pages == "Options":
    st.header("Camera Options")

    # Get available cameras
    available_cameras = get_available_cameras()
    if not available_cameras:
        st.error("No camera devices found.")
    else:
        # Save the selected camera index in session state
        st.session_state.camera_index = st.selectbox(
            'Select Camera',
            available_cameras,
            index=st.session_state.camera_index if st.session_state.camera_index in available_cameras else 0
        )
        st.success(f"Selected camera index: {st.session_state.camera_index}")

if pages == "Main":
    if st.session_state.camera_index is None:
        st.warning("Please select a camera in the Options page.")
    else:
        FRAME_WINDOW = st.image([])
        barcode_text = st.empty()

        cap = cv2.VideoCapture(st.session_state.camera_index)
        while True:
            ret, frame = cap.read()
            if not ret:
                st.error(f"Failed to capture image from camera {st.session_state.camera_index}.")
                break

            # Define crop dimensions (e.g., 50% of original width/height)
            crop_width = frame.shape[1] // 3
            crop_height = frame.shape[0] // 3

            # Crop to center
            frame_cropped = crop_center(frame, crop_width, crop_height)

            # Detect barcode within the cropped frame
            frame_cropped = detect_barcode(frame_cropped)

            # Convert to RGB for Streamlit display
            frame_cropped = cv2.cvtColor(frame_cropped, cv2.COLOR_BGR2RGB)
            FRAME_WINDOW.image(frame_cropped)

        cap.release()
