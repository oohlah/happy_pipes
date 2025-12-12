import cloudinary
import cloudinary.uploader
import os

cloudinary.config(
    cloud_name="dzibswxj0",
    api_key="193738126849429",
    api_secret="CGln5vmTC0MDMO37-fdwUdFoi8A"
)


#Image file to be uploaded
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
IMAGE_PATH = os.path.join(STATIC_DIR, "last_env_image.jpg")

#upload image and return public url - allow overwrite
def upload_image(image_path,
                 folder = "environment_camera",
                 public_id = "last_env_image"):
    result = cloudinary.uploader.upload(
        image_path,
        folder="environment_camera",
        public_id="last_env_image",
        overwrite = True,
        invalidate = True,
    )
    url = result["secure_url"]
    return url

def main():
    url = upload_image(IMAGE_PATH)
    print("Upload Complete")
    print(f"Public URL: {url}")

if __name__ == "__main__":
    main()