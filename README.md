# Image stenography

Steganography entails disguising sensitive data, by encoding it inside other
forms of media. A simple technique is to encode a message one bit at a time into
an image, by setting the least significant bit of each pixel to a single bit of
the message. To recover the message, one simply strips the LSBs in the same
order, until a delimiter is hit.

## Dependencies

This tool uses the Python Image Library, or PIL, to read and write image data. 
The Python3 fork is called Pillow, which can be installed with `pip install
Pillow`

## How it works

Image steganography gets tricky with compressed image formats like JPEG. The
only image format this tool currently supports is PNG. Using PIL, the input 
image's data is read as binary. The input message is converted into a binary
string, and encoded into the least significant bit of each pixel. Once the 
message has been fully encoded, a trailing delimiter is written.

To decode, this process is reversed: the least significant bits are read off
the image until the delimiter is hit, and the input message is recovered and
displayed.

## Examples images

There are two images included to demonstrate the visual differences. The `lime`
image demonstrates the difficulty the naked eye has in distinguishing between
original and encoded images, while the `castle` image would have a stronger
resistance to an analytical approach, as it contains a greater color palette.
