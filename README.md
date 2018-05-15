# Image stenography

Steganography is the art of hiding data in plain sight. This tool takes a PNG
image, and encodes a message one bit at a time, into the least significant bit
of each pixel of the PNG image.

## Dependencies

This tool uses the Python Image Library, or PIL. The Python3 fork Pillow, which
can be installed with `pip install Pillow`

## How it works

Image steganography gets tricky with commpressive image formats like JPEG. The
only supported image format currently is PNG. Using Python Image Library,  the
image data is read and converted to binary data. Then the message is converted
into a binary string, and encoded into the least significant bit of each pixel.

## Examples

The included images are 
