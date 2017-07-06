#!/usr/bin/python3
import argparse
import imghdr
from PIL import Image

################################################################################
# Steganography - the practice of hiding data "in plain sight"
#
#   Encodes and decodes messages hidden in the LSB of an image file 
#
#   NOTE: Currently only supports .png files, as .jpeg files have lossy
#         compression, complicating the encoding process 
################################################################################

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_image", help="Input image file", type=str)
    parser.add_argument("-m", "--message", help="Message to encode in input file", type=str)
    parser.add_argument("-d", "--decode", help="Decode input file", action="store_true")
    parser.add_argument("-o", "--output_filename", help="Name for output image", type=str,
                                          default="output.png", nargs='?')
    parser.add_argument("-v", "--verbose", help="Enable verbose output", action="store_true")
    args = parser.parse_args()

    if args.message:
        encodeMessage(args.input_image, args.output_filename, args.message, args.verbose)
    elif args.decode:
        print(extractMessage(args.input_image, args.verbose))


def toBinary(string):
    ''' Converts a string into binary of the form 0b<binary>
        
        Input: string <ascii text>
        Output: string <binary>
    '''
    return bin(int.from_bytes(string.encode(encoding="ascii"), byteorder='big'))


def toText(binaryMessage):
    ''' Converts a binary string of the form 0b<binary> into an ascii string
        If UnicodeDecodeError, then report back error
        
        Input: binary
        Output: ascii string
    '''
    try:
        string = int(binaryMessage, 2)
        return string.to_bytes((string.bit_length() + 7) // 8, byteorder='big').decode(encoding="ascii")
    except UnicodeDecodeError:
        print("No message found, are you sure your input file was properly encoded?")
        exit(3)


def encodeMessage(imageFile, outputFile, message, verbose=False):
    ''' Unpacks image, and encodes the message in LSB format

        Input: image, message in binary, image width, image height, and verbose flag
        Output: list of pixel values
    '''
    # Local variable declarations
    bitsInjected = 0
    delimBits = 0
    imageData = []

    # Check image format 
    if imghdr.what(imageFile) != "png":
        print("Sorry, but this program only supports .png image formats")
        exit(1)

    # Open input image
    image = Image.open(imageFile)

    if verbose: print("Converting \"{}\" to binary...".format(message))

    # Check message length
    binaryMessage = toBinary(message)[2:]
    if len(binaryMessage) > (image.size[0] * image.size[1] * 3):
        print("This image is too small to contain your message!\nExiting...")
        exit(2)

    if verbose: print("Encoding message...")

    # Loop through every pixel of input image
    for y in range(image.size[1]):
        for x in range(image.size[0]):
            for index, color in enumerate(image.getpixel((x,y))):

                # Encode one bit of the message string
                if bitsInjected < len(binaryMessage):
                    # Set LSB of color to one bit of the binaryMessage
                    # Mask color with 254 to gaurantee LSB is 0, then set LSB to message bit
                    imageData.append(color & 254 | int(binaryMessage[bitsInjected]))
                    bitsInjected += 1

                # Zero out 8 LSB as message delimeter
                elif delimBits < 8:
                    imageData.append(color & 254)
                    delimBits += 1
                
                # After message & delimeter are encoded, pass image data through
                else:
                    imageData.append(color)

    # Create new image file
    savedImage = Image.frombytes('RGB', image.size, bytes(imageData))

    # Ensure output file ends with ".png"
#    if not outputFile[-4:] == ".png": outputFile += ".png"
    savedImage.save(outputFile, 'PNG')

    if verbose: print("Saved encoded data as \"{}\"\nDone".format(outputFile))


def extractMessage(imageFile, verbose=False):
    ''' Extracts message from image

        Input: <input_image>, <image_size>, <verbosity_flag>
        Output: <message>
    '''
    # Initialize message
    message = ""
    # Check image format 
    if imghdr.what(imageFile) != "png":
        print("Sorry, but this program only supports .png image formats")
        exit(1)

    # Open input image
    image = Image.open(imageFile)

    if verbose: print("Extracting message...")
    byteList = getBinaryMessage(image)

    if verbose: print("Converting binary to text...")
    for byte in byteList:
        message += toText(byte)

    return message


def getBinaryMessage(image):
    ''' Stores the LSB of each color for each pixel until encountering
        a \x00 character

        Input: image <Image>
        Output: byteList [string]
    '''

    # Buffer to store message
    message = "0b0"

    # Return message after finding first \x00
    bitCount = 1

    # List of bytes to translate back into text
    byteList = []
    byte = "0"

    # Loop through picture and store all LSB in message
    for y in range(image.size[1]):
        for x in range(image.size[0]):
            for color in image.getpixel((x,y)):

                # Store last bit of pixel's color, e.g. 0b1110011(0)
                byte += bin(color)[-1]
                bitCount += 1

                # Save each character of message
                if bitCount == 8:

                    # If we encounter the end of the message
                    if byte == "00000000":
                        return byteList

                    byteList.append(byte)
                    bitCount = 0
                    byte = ""


if __name__ == "__main__":
    main()
