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
def upload_image(image_path = IMAGE_PATH, #explicitly setting image_path to IMAGE_PATH so it can be called without arguments
                 folder = "environment_camera",
                 public_id = "last_env_image"):
    result = cloudinary.uploader.upload(
        image_path, 
        folder="environment_camera",
        public_id="last_env_image",
        overwrite = True,
        invalidate = True,
    )
    url_pic = result["secure_url"]
    return url_pic


def image_url():
    return upload_image(IMAGE_PATH)

CHART_PATH = os.path.join(STATIC_DIR, "temp_and_dew_point.png")

#upload image and return public url - allow overwrite
def upload_chart(image_path=CHART_PATH,
                 folder="environment_chart",
                 public_id="temp_and_dew_point"):
   
    result = cloudinary.uploader.upload(
        image_path,
        folder=folder,
        public_id=public_id,
        overwrite=True,
        invalidate=True
    )
    url_chart = result["secure_url"]
    return url_chart

def chart_url():
    return upload_chart()

def main():
    url_pic = upload_image(IMAGE_PATH)
    print("Upload Picture Complete")
    url_chart = upload_chart(CHART_PATH)
    print(f"Public Pic URL: {url_pic}")
    print(f"Public Chart URL: {url_chart}")
    # print (image_url())



if __name__ == "__main__":
    main()