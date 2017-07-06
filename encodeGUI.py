#!/usr/bin/python3
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from steganography import encodeMessage
from PIL import Image
import sys, os, shutil

class App(QApplication):
    # Main application
    
    # Input: command line arguments <list>
    # Output: None

    def __init__(self):
        # Initialize parent widget
        QApplication.__init__(self, sys.argv)

        # Set application name
        self.setApplicationName("Encoding GUI")

        # Create main window
        self.mainWindow = MainWindow()

        # Show main window
        self.mainWindow.show()


class MainWindow(QMainWindow):
    # Main GUI window

    def __init__(self):
        
        # Initialize parent widget
        QMainWindow.__init__(self)

        # Initialize this window
        self.setWindowTitle("Message encoder")

        # Set the size of the main window
        self.resize(1080, 720)

        # Create a main widget object (the central widget)
        self.mainWidget = MainWidget()
        
        # Set main widget object as central widget of main window
        self.setCentralWidget(self.mainWidget)

        # Add file menu with exit action
        self.fileMenu = QMenu("File")
        self.exit = QAction("Exit", self)

        # Set exit icon
        self.exit.setIcon(QIcon(os.path.join(sys.path[0], "icons", "exit.png")))
        self.exit.triggered.connect(self.close) 
        self.fileMenu.addAction(self.exit)

        # Add file menu to menu bar
        self.menuBar().addMenu(self.fileMenu)

        # Add exit to tool bar
        self.toolBar = QToolBar()
        self.toolBar.addAction(self.exit)
        self.addToolBar(self.toolBar)

    def closeEvent(self, event):
        ''' Override the default close event actions. Runs whenever 
            application closes.

            Input: None
            Output: None
        '''
        if os.path.isfile(os.path.join(sys.path[0], self.mainWidget.tempImage)):
            os.remove(os.path.join(sys.path[0], self.mainWidget.tempImage))
        print("Application closed")
        QMainWindow.closeEvent(self, event)


class MainWidget(QWidget):
    # Central widget, contains widgets and layouts

    def __init__(self):
        QWidget.__init__(self)

        #####################################
        # Initialize variables/file structure
        #####################################
        self.tempImage = "tempImage.png"
        self.encodedImagesDirectory = "encodedImages"
        if not os.path.exists(os.path.join(sys.path[0], self.encodedImagesDirectory)):
            os.mkdir(os.path.join(sys.path[0], self.encodedImagesDirectory))

        ################
        # Create layouts
        ################
        self.mainLayout = QHBoxLayout(self)
        self.leftLayout = QVBoxLayout()
        self.selectorLayout = QHBoxLayout()
        self.messageLayout = QHBoxLayout()
        self.rightLayout = QVBoxLayout()
        self.saveFileLayout = QHBoxLayout()

#        self.leftLayout.setSizePolicy(QSizePolicy.QSizePolicy(minimum, minimum))

        #########################
        # Left side functionality
        #########################

        # Setup image selector combobox
        self.imageSelector = QComboBox()
            # Path to image directory
        self.imagePath = os.path.join(sys.path[0], "images")
            # Add all images to imageSelector 
        self.imageSelector.addItems(os.listdir(self.imagePath))
            # Change image when selected in ComboBox, and initialize right image label
        self.embeddedImageLabel = QLabel()
        self.imageSelector.currentTextChanged.connect(self.showImage)

        # Line edit for message
        self.inputMessage = QLineEdit(placeholderText="Message")

        # Setup image preview
            # Create label to display image in
        self.imageLabel = QLabel()
        self.imageLabel.setScaledContents(True)
            # Initialize image object
        self.imageObject = QImage()
            # Initialize QImageReader
        self.imageReader = QImageReader()

        # Push button to encode message
        buttonText = "Encode Message"
        self.generateEncodedImageButton = QPushButton(buttonText)
            # Set button width
        width = self.generateEncodedImageButton.fontMetrics().boundingRect(buttonText).width() + 7
        self.generateEncodedImageButton.setMaximumWidth(width)
            # Link button with functionality
        self.generateEncodedImageButton.clicked.connect(self.generateEncodedImage)

        ###########################
        # Create vertical separator
        ###########################
        self.verticalSeparator = QFrame()
        self.verticalSeparator.setFrameStyle(QFrame.VLine)
        self.verticalSeparator.setFrameShadow(QFrame.Sunken)

        #########################
        # Right side functioality
        #########################

        # Setup encoded image display label
        self.embeddedImageLabel.setScaledContents(True)
        # Initialize image object
        self.embeddedImageObject = QImage()

        # Line edit to name output image
        self.nameOutputImage = QLineEdit(placeholderText="Output image name")
        self.nameOutputImage.setText("output.png")
        buttonText = "Save encoded image"
        self.saveImageButton = QPushButton(buttonText)
        width = self.saveImageButton.fontMetrics().boundingRect(buttonText).width() + 7
        self.saveImageButton.setMaximumWidth(width)
        self.saveImageButton.clicked.connect(self.saveImage)

        #####################################
        # Compile everything into Main Layout
        #####################################
            # Left side
        self.mainLayout.addLayout(self.leftLayout)
        self.leftLayout.addLayout(self.selectorLayout)
        self.leftLayout.addStretch(0)
        self.leftLayout.addWidget(self.imageLabel)
        self.leftLayout.addStretch(0)
        self.leftLayout.addLayout(self.messageLayout)
        self.selectorLayout.addWidget(self.imageSelector)
        self.messageLayout.addWidget(self.inputMessage) 
        self.messageLayout.addWidget(self.generateEncodedImageButton)#, alignment=Qt.AlignLeft) 
            # Centerline separator
        self.mainLayout.addWidget(self.verticalSeparator, alignment=Qt.AlignHCenter)
            # Right side
        self.mainLayout.addLayout(self.rightLayout)
#        self.rightLayout.addStretch(0)
        self.rightLayout.addWidget(self.embeddedImageLabel, alignment=Qt.AlignBottom)
        self.rightLayout.addLayout(self.saveFileLayout)
        self.saveFileLayout.addWidget(self.nameOutputImage)
        self.saveFileLayout.addWidget(self.saveImageButton)

        # Display image
        self.showImage()



    def showImage(self):
        ''' Clears the right image, and displays the selected image on left side
            
            Input: None
            Output: None
        '''
        # Store path to selected image file
        selectedImagePath = os.path.join(self.imagePath, self.imageSelector.currentText())

        # Set label to image size
        image = Image.open(selectedImagePath)
        self.imageLabel.setFixedSize(image.size[0], image.size[1])

        # Display image
        self.imageLabel.setPixmap(QPixmap(selectedImagePath))

        # Adjust QLineEdit lengths to match image width
        self.inputMessage.setFixedWidth(self.imageLabel.width() - self.generateEncodedImageButton.width())
        self.nameOutputImage.setFixedWidth(self.imageLabel.width() - self.saveImageButton.width())

        # Set up right side image label
        self.embeddedImageLabel.setFixedSize(image.size[0], image.size[1])
        self.embeddedImageLabel.setText("Encode a message to see resulting image")


    def generateEncodedImage(self):
        ''' Passes the message string and selected image to steganography
            program, and displays the resultant image
            
            Input: None
            Output: None
        '''
        encodeMessage(os.path.join(self.imagePath, self.imageSelector.currentText()),
                      os.path.join(sys.path[0], self.tempImage), self.inputMessage.displayText())

        self.embeddedImageLabel.setPixmap(QPixmap(os.path.join(sys.path[0], self.tempImage)))

    def saveImage(self):
        ''' Copies the currently displayed encoded image to the output name of user's choice

            Input: None
            Output: None
        '''
        outputFileName = self.nameOutputImage.displayText()
        if not outputFileName[-4:] == ".png": outputFileName += ".png"
        shutil.copy(os.path.join(sys.path[0], self.tempImage),
                    os.path.join(sys.path[0], self.encodedImagesDirectory, outputFileName))


def main():
    # Create application
    app = App()

    # Start event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
