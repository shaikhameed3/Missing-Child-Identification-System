import cv2
import dlib
import numpy as np


# Paths to the dlib model files
LANDMARK_MODEL = "models/shape_predictor_68_face_landmarks.dat"
FACE_RECOGNITION_MODEL = "models/dlib_face_recognition_resnet_model_v1.dat"


# Load dlib models
face_detector = dlib.get_frontal_face_detector()

shape_predictor = dlib.shape_predictor(
    LANDMARK_MODEL
)

face_recognition_model = dlib.face_recognition_model_v1(
    FACE_RECOGNITION_MODEL
)


def get_embedding(face):
    """
    Convert a detected face into a 128-dimensional
    dlib facial embedding.
    """

    if face is None:
        raise ValueError("No face was provided.")

    # Convert to NumPy array
    face = np.asarray(face)

    # Make sure image is RGB
    if len(face.shape) != 3:
        raise ValueError("Invalid face image.")

    # Resize face
    face = cv2.resize(
        face,
        (150, 150)
    )

    # Detect face using dlib
    detections = face_detector(
        face,
        1
    )

    # If dlib cannot detect the face in the
    # already cropped MTCNN face, use the
    # complete image as the face rectangle.
    if len(detections) == 0:

        height, width = face.shape[:2]

        rectangle = dlib.rectangle(
            0,
            0,
            width - 1,
            height - 1
        )

    else:

        rectangle = max(
            detections,
            key=lambda r: r.width() * r.height()
        )

    # Detect 68 facial landmarks
    shape = shape_predictor(
        face,
        rectangle
    )

    # Generate 128-dimensional embedding
    embedding = face_recognition_model.compute_face_descriptor(
        face,
        shape
    )

    return np.asarray(
        embedding,
        dtype=np.float32
    )