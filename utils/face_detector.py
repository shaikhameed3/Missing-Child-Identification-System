import cv2
from mtcnn import MTCNN


# Create MTCNN detector
detector = MTCNN()


def detect_face(image_path):
    """
    Detect the largest/highest-confidence face
    from an image using MTCNN.

    Returns:
        Cropped RGB face image, or None if no face is detected.
    """

    image = cv2.imread(image_path)

    if image is None:
        raise ValueError("Could not read the image.")

    # OpenCV loads images as BGR.
    # MTCNN expects RGB.
    rgb_image = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2RGB
    )

    # Detect faces
    detections = detector.detect_faces(rgb_image)

    if not detections:
        return None

    # Select the face with highest confidence
    best_face = max(
        detections,
        key=lambda item: item.get("confidence", 0)
    )

    x, y, width, height = best_face["box"]

    # Prevent negative coordinates
    x = max(0, x)
    y = max(0, y)

    x2 = min(
        rgb_image.shape[1],
        x + width
    )

    y2 = min(
        rgb_image.shape[0],
        y + height
    )

    face = rgb_image[y:y2, x:x2]

    if face.size == 0:
        return None

    return face