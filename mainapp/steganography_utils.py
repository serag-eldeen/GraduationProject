from PIL import Image

# Generate data in binary format
def genData(data):
    return [format(ord(i), '08b') for i in data]

# Modify the pixels according to the data
def modPix(pix, data):
    datalist = genData(data)
    lendata = len(datalist)
    imdata = iter(pix)

    for i in range(lendata):
        pix = [value for value in imdata.__next__()[:3] +
                        imdata.__next__()[:3] +
                        imdata.__next__()[:3]]

        for j in range(8):
            original_lsb = pix[j] % 2
            if datalist[i][j] == '0' and original_lsb != 0:
                pix[j] -= 1
            elif datalist[i][j] == '1' and original_lsb == 0:
                pix[j] = pix[j] - 1 if pix[j] != 0 else pix[j] + 1

        if i == lendata - 1:
            pix[-1] = pix[-1] - 1 if pix[-1] % 2 == 0 else pix[-1] + 1
        else:
            pix[-1] = pix[-1] - 1 if pix[-1] % 2 != 0 else pix[-1]

        pix = tuple(pix)
        yield pix[:3]
        yield pix[3:6]
        yield pix[6:9]

# Calculate the maximum number of characters that can be embedded
def max_characters(image_path):
    img = Image.open(image_path)
    width, height = img.size
    total_pixels = width * height
    max_chars = total_pixels // 3
    return max_chars


# Encode the image with the data
def encode_enc(newimg, data):
    w = newimg.size[0]
    (x, y) = (0, 0)

    for pixel in modPix(newimg.getdata(), data):
        newimg.putpixel((x, y), pixel)
        x = 0 if x == w - 1 else x + 1
        y += 1 if x == 0 else 0

# Function to encode data into an image
def encode(image_path, output_image_path, data):
    if not data:
        raise ValueError("Data is empty")

    img = Image.open(image_path)
    newimg = img.copy()
    encode_enc(newimg, data)
    newimg.save(output_image_path)
    print(f"Message encoded successfully! Saved as {output_image_path}")

# Decode the data from the image
def decode(image_path):
    img = Image.open(image_path)
    data = ''
    imgdata = iter(img.getdata())

    while True:
        pixels = [value for value in imgdata.__next__()[:3] +
                                imgdata.__next__()[:3] +
                                imgdata.__next__()[:3]]
        binstr = ''.join([str(i % 2) for i in pixels[:8]])
        data += chr(int(binstr, 2))

        if pixels[-1] % 2 != 0:
            return data
