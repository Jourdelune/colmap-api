import os
import sys
import requests


def post_images_to_api(images_dir, api_url="http://localhost:8000/sfm", multiply=1):
    files = []
    image_files = [
        f
        for f in os.listdir(images_dir)
        if os.path.isfile(os.path.join(images_dir, f))
        and f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]
    if not image_files:
        print("No images found in the directory.")
        return

    for i in range(multiply):
        for filename in image_files:
            filepath = os.path.join(images_dir, filename)
            # Ajoute un suffixe pour éviter les collisions de noms lors de la duplication
            send_name = (
                f"{os.path.splitext(filename)[0]}_copy{i}{os.path.splitext(filename)[1]}"
                if multiply > 1
                else filename
            )
            files.append(("images", (send_name, open(filepath, "rb"), "image/jpeg")))

    response = requests.post(api_url, files=files)
    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.text}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python post_images.py <images_directory> [multiply]")
        sys.exit(1)
    images_dir = sys.argv[1]
    multiply = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    post_images_to_api(images_dir, multiply=multiply)
