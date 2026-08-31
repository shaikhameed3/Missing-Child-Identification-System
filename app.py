from flask import Flask, render_template, request, redirect, url_for, flash
import os
import json

from utils.face_detector import detect_face
from utils.face_embedding import get_embedding
from utils.face_matcher import add_embedding, find_matches


app = Flask(__name__)

app.secret_key = "missing-child-demo-key"


# ============================================================
# PROJECT FOLDERS
# ============================================================

UPLOAD_FOLDER = "uploads"
REGISTERED_FOLDER = "registered_faces"
DATABASE_FOLDER = "database"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REGISTERED_FOLDER, exist_ok=True)
os.makedirs(DATABASE_FOLDER, exist_ok=True)


# ============================================================
# DATABASE FILE
# ============================================================

DATABASE_FILE = os.path.join(
    DATABASE_FOLDER,
    "children.json"
)


# Create database if it doesn't exist
if not os.path.exists(DATABASE_FILE):

    with open(DATABASE_FILE, "w") as file:
        json.dump([], file)


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# ============================================================
# REGISTER CHILD
# ============================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        # Get form data
        name = request.form.get("name")
        age = request.form.get("age")
        gender = request.form.get("gender")
        missing_date = request.form.get("missing_date")
        missing_location = request.form.get("missing_location")

        # Get uploaded image
        image = request.files.get("image")


        # Check required fields
        if not name or not image:

            flash("Name and image are required.")

            return redirect(
                url_for("register")
            )


        # ====================================================
        # SAVE IMAGE
        # ====================================================

        filename = image.filename

        image_path = os.path.join(
            REGISTERED_FOLDER,
            filename
        )

        image.save(image_path)


        # ====================================================
        # FACE DETECTION + EMBEDDING
        # ====================================================

        try:

            face = detect_face(
                image_path
            )

            if face is None:

                flash(
                    "No face detected in the uploaded image."
                )

                return redirect(
                    url_for("register")
                )


            embedding = get_embedding(
                face
            )


        except Exception as e:

            flash(
                f"Face processing failed: {e}"
            )

            return redirect(
                url_for("register")
            )


        # ====================================================
        # READ EXISTING RECORDS
        # ====================================================

        with open(
            DATABASE_FILE,
            "r"
        ) as file:

            children = json.load(file)


        # ====================================================
        # CREATE NEW CHILD ID
        # ====================================================

        child_id = len(children) + 1


        # ====================================================
        # CREATE CHILD RECORD
        # ====================================================

        child = {

            "id": child_id,

            "name": name,

            "age": age,

            "gender": gender,

            "missing_date": missing_date,

            "missing_location": missing_location,

            "image": image_path
        }


        # Add child to database
        children.append(
            child
        )


        # Save database
        with open(
            DATABASE_FILE,
            "w"
        ) as file:

            json.dump(
                children,
                file,
                indent=4
            )


        # ====================================================
        # SAVE FACIAL EMBEDDING
        # ====================================================

        add_embedding(
            child_id,
            embedding
        )


        # ====================================================
        # SUCCESS
        # ====================================================

        flash(
            "Child registered successfully."
        )

        return redirect(
            url_for("home")
        )


    # GET request
    return render_template(
        "register.html"
    )


# ============================================================
# SEARCH CHILD
# ============================================================

@app.route(
    "/search",
    methods=["POST"]
)
def search():

    # Get uploaded image
    image = request.files.get(
        "image"
    )


    # Check image
    if not image:

        flash(
            "Please upload an image."
        )

        return redirect(
            url_for("home")
        )


    # ========================================================
    # SAVE SEARCH IMAGE
    # ========================================================

    filename = image.filename

    image_path = os.path.join(
        UPLOAD_FOLDER,
        filename
    )

    image.save(
        image_path
    )


    # ========================================================
    # FACE DETECTION
    # ========================================================

    try:

        face = detect_face(
            image_path
        )


        if face is None:

            flash(
                "No face detected in the uploaded image."
            )

            return redirect(
                url_for("home")
            )


        # ====================================================
        # CREATE QUERY EMBEDDING
        # ====================================================

        query_embedding = get_embedding(
            face
        )


        # ====================================================
        # FIND MATCHES
        # ====================================================

        matches = find_matches(
            query_embedding,
            top_k=5
        )


    except Exception as e:

        flash(
            f"Face matching failed: {e}"
        )

        return redirect(
            url_for("home")
        )


    # ========================================================
    # LOAD CHILD DATABASE
    # ========================================================

    with open(
        DATABASE_FILE,
        "r"
    ) as file:

        children = json.load(
            file
        )


    # ========================================================
    # CREATE MATCHED CHILD LIST
    # ========================================================

    matched_children = []


    for match in matches:

        for child in children:

            if child["id"] == match["id"]:

                child_copy = child.copy()


                # Convert similarity to percentage
                child_copy["similarity"] = round(
                    match["similarity"] * 100,
                    2
                )


                matched_children.append(
                    child_copy
                )

                break


    # ========================================================
    # DISPLAY RESULTS
    # ========================================================

    return render_template(

        "results.html",

        children=matched_children,

        uploaded_image=image_path
    )


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )