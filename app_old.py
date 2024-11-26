import cv2
import streamlit as st
from pyzbar.pyzbar import decode
import requests


def get_book_details(isbn):
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        results = response.json()
        if results.get("totalItems", 0) > 0:
            book = results["items"][0]
            volume_info = book.get("volumeInfo", {})
            book_details = {
                "TITEL": volume_info.get("title", "N/A"),
                "ONDERKOP": volume_info.get("subtitle", "N/A"),
                "AUTEUR": ", ".join(volume_info.get("authors", ["Unknown"])),
                "PUBLICATIEDATUM": volume_info.get("publishedDate", "N/A"),
                "BESCHRIJVING": volume_info.get("description", "N/A"),
                "ISBN_10": next(
                    (id["identifier"] for id in volume_info.get("industryIdentifiers", []) if id["type"] == "ISBN_10"),
                    "N/A"),
                "ISBN_13": next(
                    (id["identifier"] for id in volume_info.get("industryIdentifiers", []) if id["type"] == "ISBN_13"),
                    "N/A"),
                "AANTAL_PAGINA'S": volume_info.get("pageCount", "N/A"),
                "TAAL": volume_info.get("language", "N/A"),
            }
            return book_details
        else:
            print("No book found for the given ISBN.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching book details: {e}")
        return None


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
            text = f"{barcode_data} ({barcode.type})"
            cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            book_details = get_book_details(barcode_data)
            if book_details:
                table_html = "<table>"
                for key, value in book_details.items():
                    table_html += f"<tr><td><b>{key}</b></td><td>{value}</td></tr>"
                table_html += "</table>"
                st.session_state.book_table.markdown(table_html, unsafe_allow_html=True)
    return frame


if "camera_index" not in st.session_state:
    st.session_state.camera_index = 0
if "book_table" not in st.session_state:
    st.session_state.book_table = st.empty()

pages = st.sidebar.radio("Navigation", ["Main", "Options"])
if pages == "Options":
    st.header("Camera Options")
    available_cameras = get_available_cameras()
    if not available_cameras:
        st.error("No camera devices found.")
    else:
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
        cap = cv2.VideoCapture(st.session_state.camera_index)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                st.error(f"Failed to capture image from camera {st.session_state.camera_index}.")
                break
            crop_width = frame.shape[1] // 2
            crop_height = frame.shape[0] // 2
            frame_cropped = crop_center(frame, crop_width, crop_height)
            frame_cropped = detect_barcode(frame_cropped)
            frame_cropped = cv2.cvtColor(frame_cropped, cv2.COLOR_BGR2RGB)
            FRAME_WINDOW.image(frame_cropped)
        cap.release()
