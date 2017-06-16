#!/usr/bin/python3
import argparse
import imghdr
from PIL import Image

################################################################################
# Steganography - the practice of hiding data "in plain sight"
#   Encodes a message string into an image by manipulating the naked eye's
#   inability to decipher a 1-bit difference in a pixel's color
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
###############
    message = "TTT"
    bMessage = "0b1010100"
    print(toBinary(message, args.verbose))
    print(bMessage)
    print(toText(bMessage, args.verbose))
###############

    ###########################
    # Encode message into image
    ###########################
    if args.message:
        # Cut the leading '0b' off of the message
        binaryMessage = toBinary(args.message, args.verbose)[2:]

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
            savedImage.show()
            print("Saved encoded data as \"{}.png\"".format(args.output_filename))

    ###########################
    # Decode message from image
    ###########################
    elif args.decode:
        message = extractMessage(image, image.size, args.verbose)
        print("hidden message:\n{}".format(message))
        
    


def toBinary(string, verbose):
    ''' Converts a string into binary of the form 0b<binary>
        
        Input: ascii string
        Output: binary translation
    '''
    if verbose: print("Converted \"{}\" to binary".format(string))

    return bin(int.from_bytes(string.encode(encoding="ascii"), byteorder='big'))


def toText(binaryMessage, verbose):
    ''' Converts a binary string of the form 0b<binary> into an ascii string
        
        Input: binary
        Output: ascii string
    '''
    if verbose: print("Converted binary to text")

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
    message = "0b"

    # Return message after finding first \x00
    bitCounter = 0
    zeroCounter = 0

    # Loop through picture and store all LSB in message
    for y in range(size[1]):
        for x in range(size[0]):
            for color in image.getpixel((x,y)):
                message += str(color & 1)
                bitCounter += 1
                if(str(color&1) == "0"):
                    zeroCounter += 1

                # Return once reaching a null character
                if bitCounter == 8 and zeroCounter == 8:
                    return toText(message, verbose)
                else:
                    bitCounter = zeroCounter = 0
                    

    print(message)
    return toText(message, verbose)
    

if __name__ == "__main__":
    main()
