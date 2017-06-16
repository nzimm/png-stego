#!/usr/bin/python3
import argparse
import imghdr
from PIL import Image

################################################################################
# Steganography - the practice of hiding data "in plain sight"
#
#   Encodes and decodes messages hidden in the LSB of an image file 
#
#   NOTE: Currently only supports .png files, the complexity of the encoding
#         algorithm is much greater for compressive image files
################################################################################

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_image", help="Input image file", type=str)
    parser.add_argument("-m", "--message", help="Message to encode in input file", type=str)
    parser.add_argument("-d", "--decode", help="Decode input file", action="store_true")
    parser.add_argument("-o", "--output_filename", help="Name for output image", type=str,
                                          default="output", nargs='?')
    parser.add_argument("-v", "--verbose", help="Enable verbose output", action="store_true")
    args = parser.parse_args()

    # Supported image types
    if imghdr.what(args.input_image) != "png":
        print("Sorry, but this program only supports .png image formats")
        exit(1)

    # Prime input image
    image = Image.open(args.input_image)

    ###############################################################################
    # Encode message into image
    ###############################################################################
    if args.message:

        if args.verbose: print("Converting \"{}\" to binary".format(args.message))
        binaryMessage = toBinary(args.message)[2:]

        # Check if picture has enough pixels to store message
        image = Image.open(args.input_image)
        xMax, yMax = image.size
        if len(binaryMessage) > (xMax * yMax * 3):
            print("This image is too small to contain your message!\nExiting...")
            exit(2)

        encodedPixelData = encodeMessage(image, binaryMessage, image.size, args.verbose)
        savedImage = Image.frombytes('RGB', image.size, bytes(encodedPixelData))
        savedImage.save(args.output_filename + '.png', 'PNG')
        if args.verbose:
            print("Saved encoded data as \"{}.png\"".format(args.output_filename))

    ###############################################################################
    # Decode message from image
    ###############################################################################
    elif args.decode:
        byteList = extractMessage(image, image.size, args.verbose)
        message = "" 
        if args.verbose: print("Converting binary to text")
        for byte in byteList:
            message += toText(byte)
        print("hidden message:\n{}".format(message))
        
    


def toBinary(string):
    ''' Converts a string into binary of the form 0b<binary>
        
        Input: ascii string
        Output: binary translation
    '''
    return bin(int.from_bytes(string.encode(encoding="ascii"), byteorder='big'))


def toText(binaryMessage):
    ''' Converts a binary string of the form 0b<binary> into an ascii string
        
        Input: binary
        Output: ascii string
    '''
    string = int(binaryMessage, 2)
    return string.to_bytes((string.bit_length() + 7) // 8, byteorder='big').decode(encoding="ascii")


def encodeMessage(image, binaryMessage, size, verbose):
    ''' Unpacks image, and encodes the message in LSB format

        Input: image, message in binary, image width, image height, and verbose flag
        Output: list of pixel values
    '''
    if verbose: print("Encoding message...")

    # How much of message has been encoded
    bitsInjected = 0

    # Byte buffer for pixel data
    imageData = []

    # Loop through every pixel of input image
    for y in range(size[1]):
        for x in range(size[0]):
            for index, color in enumerate(image.getpixel((x,y))):

                # Encode LSB to one bit of the message string
                if bitsInjected < len(binaryMessage):
                    imageData.append(((color >> 1) << 1) | int(binaryMessage[bitsInjected]))
                    bitsInjected += 1

                # Zero out LSB after message has been fully encrypted
                else:
                    imageData.append(color & 254)

    if verbose: print("Encoding complete")
    return imageData

def extractMessage(image, size, verbose):
    ''' Extracts message from image

        Input: <input_image>, <image_size>, <verbosity_flag>
        Output: <message>
    '''
    if verbose: print("Extracting message...")

    # Buffer to store message
    message = "0b0"

    # Return message after finding first \x00
    bitCount = 1

    # List of bytes to translate back into text
    byteList = []
    byte = ""

    # Loop through picture and store all LSB in message
    for y in range(size[1]):
        for x in range(size[0]):
            for color in image.getpixel((x,y)):

                # One bit of the message
                byte += str(color & 1)
                bitCount += 1

                # Save each character of message
                if bitCount == 8:

                    # If we encounter the end of the message
                    if byte == "00000000":
                        return byteList

                    byteList.append(byte)
                    bitCount = 0
                    byte = ""
                    
    return byteList
    

if __name__ == "__main__":
    main()
