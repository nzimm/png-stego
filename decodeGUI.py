#!/usr/bin/python3
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from steganography import extractMessage
from PIL import Image
import sys, os

class App(QApplication):
    # Main application

    # Input: command line arguments <list>
    # Output: None

    def __init__(self):
        # Initialize parent widget
        QApplication.__init__(self, sys.argv)

        # Set application name
        self.setApplicationName("Decoding GUI")

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
        self.setWindowTitle("Message decoder")

        # Set the size of the main window
        self.resize(360, 360)

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
        print("Application closed")
        QMainWindow.closeEvent(self, event)


class MainWidget(QWidget):
    # Central widget, contains widgets and layouts

    def __init__(self):
        QWidget.__init__(self)
        self.mainLayout = QVBoxLayout(self)

        #####################################
        # Initialize variables/file structure
        #####################################
        self.encodedImagesDirectory = "encodedImages"
        if not os.path.exists(os.path.join(sys.path[0], self.encodedImagesDirectory)):
            os.mkdir(os.path.join(sys.path[0], self.encodedImagesDirectory))

        
        # Setup image selector combobox
        self.imageSelector = QComboBox()
            # Path to image directory
        self.imagePath = os.path.join(sys.path[0], "encodedImages")
            # Add all images to imageSelector 
        self.imageSelector.addItems(os.listdir(self.imagePath))

        # Initialize image label and update image when selected in ComboBox
        self.imageLabel = QLabel()
        self.messageLabel = QLabel()
        self.imageSelector.currentTextChanged.connect(self.showImage)

        self.showImage()

        #####################
        # Compile Main Layout
        #####################
        self.mainLayout.addWidget(self.imageSelector)
        self.mainLayout.addWidget(self.imageLabel)
        self.mainLayout.addWidget(self.messageLabel)




    def showImage(self):
        ''' Displays the image selected in the imageSelector combobox, and
            decodes the message for viewing
            
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

        # Display message
        self.messageLabel.setText(extractMessage(selectedImagePath))


def main():
    # Create application
    app = App()

    # Start event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

