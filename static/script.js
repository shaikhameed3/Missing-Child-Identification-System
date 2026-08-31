// Image preview

const imageInput = document.getElementById("image");

if (imageInput) {

    imageInput.addEventListener("change", function () {

        const file = this.files[0];

        if (!file) {
            return;
        }

        // Check that the selected file is an image
        if (!file.type.startsWith("image/")) {
            alert("Please select an image file.");
            this.value = "";
            return;
        }

        console.log("Selected image:", file.name);

    });

}