import cv2
import streamlit as st
from pyzbar.pyzbar import decode
import requests


def get_book_details(isbn):
    """
    Fetches book details from the Google Books API using the provided ISBN.

    Args:
        isbn (str): The ISBN code of the book to look up.

    Returns:
        dict: A dictionary containing the book details, or None if no book is found.
    """
    # Base URL for Google Books API
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"

    try:
        # Fetch response from the API
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        results = response.json()

        # Check if the ISBN returns any results
        if results.get("totalItems", 0) > 0:
            book = results["items"][0]  # Get the first (and only) result

            # Extract book details
            volume_info = book.get("volumeInfo", {})
            access_info = book.get("accessInfo", {})

            title = volume_info.get("title", "N/A")
            subtitle = volume_info.get("subtitle", "N/A")
            authors = volume_info.get("authors", [])
            print_type = volume_info.get("printType", "N/A")
            page_count = volume_info.get("pageCount", "N/A")
            publisher = volume_info.get("publisher", "N/A")
            published_date = volume_info.get("publishedDate", "N/A")
            web_reader_link = access_info.get("webReaderLink", "N/A")

            # Compile book details into a dictionary
            book_details = {
                "title": volume_info.get("title", "N/A"),
                "subtitle": volume_info.get("subtitle", "N/A"),
                "author": ", ".join(volume_info.get("authors", ["Unknown"])),
                "publishedDate": volume_info.get("publishedDate", "N/A"),
                "description": volume_info.get("description", "N/A"),
                "isbn_10": next(
                    (id["identifier"] for id in volume_info.get("industryIdentifiers", []) if id["type"] == "ISBN_10"),
                    "N/A"),
                "isbn_13": next(
                    (id["identifier"] for id in volume_info.get("industryIdentifiers", []) if id["type"] == "ISBN_13"),
                    "N/A"),
                "pageCount": volume_info.get("pageCount", "N/A"),
                "language": volume_info.get("language", "N/A"),
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
            barcode_type = barcode.type
            text = f"{barcode_data} ({barcode_type})"
            cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            book_details = get_book_details(barcode_data)
            barcode_text.write(f"Detected Book: {book_details}")
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
