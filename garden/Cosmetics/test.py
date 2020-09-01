from PIL import Image

file = 'upload/2.jpg'
img = Image.open(file)
resize_img = img.resize((2000, 2000), Image.ANTIALIAS)
resize_img.save('upload/22.jpg')