from PIL import Image
import os

def resize_image(input_image_path, output_image_path, size):
    original_image = Image.open(input_image_path)
    width, height = original_image.size
    aspect_ratio = width / height

    new_width = size
    new_height = size

    if aspect_ratio > 1:
        new_width = size
        new_height = int(size / aspect_ratio)
    elif aspect_ratio < 1:
        new_height = size
        new_width = int(size * aspect_ratio)

    resized_image = original_image.resize((new_width, new_height))

    new_image = Image.new("RGB", (size, size))
    new_image.paste(resized_image, ((size - new_width) // 2, (size - new_height) // 2))

    new_image.save(output_image_path)

# 您可以將以下程式碼替換為您的圖片路徑
input_dir = 'C:/Python/OIDv4_ToolKit/OID/Dataset/validation/Pumpkin'
output_dir = 'C:/Python/OIDv4_ToolKit/OID/DatasetAdjusted/validation/Pumpkin'

if __name__ == '__main__':

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            input_image_path = os.path.join(input_dir, filename)
            output_image_path = os.path.join(output_dir, filename)
            resize_image(input_image_path, output_image_path, 640)