import os
import sys
import threading
from datetime import datetime
from pathlib import Path

import google.generativeai as genai
from PyQt6.QtCore import QEvent, QPoint, QSize, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import (QAction, QColor, QFont, QGuiApplication, QIcon,
                         QPalette, QPixmap)
from PyQt6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
                             QLineEdit, QMainWindow, QMenu, QPushButton,
                             QSystemTrayIcon, QTextEdit, QVBoxLayout, QWidget)

from persona import Persona, PersonalityTrait


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', Path(__file__).parent)
    return Path(base_path) / relative_path

# Example usage for loading 'nigel.png'
image_path = resource_path("nigel.png")
# print(f"Image path: {image_path}")

# Configure Gemini API
MODEL_NAME = "gemini-2.0-flash"
genai.configure(api_key="AIzaSyDWI4MZGoes22zdtD6JQcsU1Y8AOb5AoDY")

# Initialize persona
nigel_persona = Persona(
    name="Nigel",
    description="A friendly and knowledgeable AI assistant with a unique personality.",
    personality_traits=[
        PersonalityTrait(
            name="Friendliness",
            description="Always maintains a warm and approachable demeanor",
            strength=0.9,
            influence=0.8
        ),
        PersonalityTrait(
            name="Knowledge",
            description="Possesses extensive knowledge across various domains",
            strength=0.8,
            influence=0.7
        )
    ]
)

# Function to interact with Gemini API
def ask_gemini(question):
    model = genai.GenerativeModel(MODEL_NAME)
    
    # Get persona context
    persona_context = nigel_persona.get_full_context()
    
    # Construct the prompt with persona context
    prompt = f"""Context about who I am:
{persona_context}

User's question: {question}

Please respond as Nigel, taking into account my personality traits and knowledge. Be consistent with my character."""

    response = model.generate_content(prompt)
    
    # Record the conversation
    nigel_persona.record_conversation(question, response.text)
    
    # Save persona state after each interaction
    nigel_persona.save_state()
    
    return response.text

# Create or get the icon path
def get_icon_path(icon):
    # Use a pre-existing system icon for simplicity
    # You can replace this with your own custom icon later
    return image_path

# Custom dropdown widget that appears from the system tray
class NiGELDropdown(QMainWindow):
    # Define signals at class level
    response_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Connect signals to handlers
        self.response_signal.connect(self.handle_response)
        self.error_signal.connect(self.handle_error)
        
        # Set fixed size window
        self.setFixedSize(400, 500)
        
        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.border_radius = 12
        self.border_width = 2
        self.border_color = "#000000"
        
        # Apply style to the main container
        self.central_widget.setStyleSheet("""
            background-color: #2D2D2D;
            border-radius: 12px;
            color: white;
        """)
        
        # Main vertical layout
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Header section
        header_layout = QHBoxLayout()
        
        # User icon/avatar
        self.user_avatar = QLabel()
        avatar_pixmap = QPixmap(get_icon_path("nigel.png"))
        self.user_avatar.setPixmap(avatar_pixmap)
        self.user_avatar.setScaledContents(True)
        self.user_avatar.setFixedSize(32, 32)
        self.user_avatar.setStyleSheet("border-radius: 16px;")
        
        # User name/email
        user_info_layout = QVBoxLayout()
        self.user_name = QLabel("NiGEL AI")
        self.user_name.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.user_status = QLabel("Active")
        self.user_status.setStyleSheet("font-size: 12px; color: #AAAAAA;")
        
        user_info_layout.addWidget(self.user_name)
        user_info_layout.addWidget(self.user_status)
        
        # Close button
        self.close_button = QPushButton("×")
        self.close_button.setStyleSheet("""
            QPushButton {
                font-size: 20px;
                color: #AAAAAA;
                border: none;
                padding: 5px;
            }
            QPushButton:hover {
                color: white;
            }
        """)
        self.close_button.clicked.connect(self.hide)
        
        header_layout.addWidget(self.user_avatar)
        header_layout.addLayout(user_info_layout)
        header_layout.addStretch()
        header_layout.addWidget(self.close_button)
        
        main_layout.addLayout(header_layout)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #3D3D3D; margin: 10px 0;")
        main_layout.addWidget(separator)
        
        # Conversation display
        self.conversation = QTextEdit()
        self.conversation.setReadOnly(True)
        self.conversation.setStyleSheet("""
            QTextEdit {
                background-color: #333333;
                border-radius: 8px;
                padding: 10px;
                color: white;
                font-size: 14px;
            }
        """)
        self.conversation.setPlaceholderText("They're Dugongs! ...")
        
        # Welcome message
        self.conversation.append("<span style='color: #AAAAAA;'>Nigel:</span> 👋 Hello, Poppet! Come on now, tell Nigel whats on your mind!")
        
        main_layout.addWidget(self.conversation)
        
        # Input area
        input_layout = QHBoxLayout()
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your message...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #333333;
                border-radius: 8px;
                padding: 10px 15px;
                color: white;
                font-size: 14px;
            }
        """)
        self.input_field.returnPressed.connect(self.send_message)
        
        self.send_button = QPushButton("Send")
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #5D5FEF;
                color: white;
                border-radius: 8px;
                padding: 10px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4D4FDF;
            }
            QPushButton:pressed {
                background-color: #3D3FCF;
            }
        """)
        self.send_button.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)
        
        main_layout.addLayout(input_layout)
        
        # Arrow indicator (points to the tray icon)
        self.arrow = QLabel()
        arrow_pixmap = QPixmap(20, 10)
        arrow_pixmap.fill(Qt.GlobalColor.transparent)
        self.arrow.setPixmap(arrow_pixmap)
        self.arrow.setStyleSheet("""
            background-color: #2D2D2D;
            border-top-left-radius: 5px;
            border-top-right-radius: 5px;
        """)
        
        # Initialize variables
        self.is_processing = False
        
    def send_message(self):
        if self.is_processing:
            return
            
        message = self.input_field.text().strip()
        if not message:
            return
            
        # Display user message
        self.conversation.append(f"<span style='color: white; font-weight: bold;'>You:</span> {message}")
        self.input_field.clear()
        
        # Indicate processing
        self.is_processing = True
        self.conversation.append("<span style='color: #AAAAAA;'>Nigel is thinking...</span>")
        
        # Use previously defined class signals
        
        # Process in a separate thread to keep UI responsive
        def process_message():
            try:
                response = ask_gemini(message)
                # Use signals to update UI in main thread
                self.response_signal.emit(response)
            except Exception as e:
                # Use signals to update UI in main thread
                self.error_signal.emit(str(e))
        
        thread = threading.Thread(target=process_message)
        thread.daemon = True
        thread.start()
    
    def handle_response(self, response):
        """Handle response from Gemini API"""
        # Remove "thinking" message
        text = self.conversation.toPlainText()
        text = text.replace("Nigel is thinking...", "")
        self.conversation.setPlainText(text)
        
        # Add response
        self.conversation.append(f"<span style='color: #AAAAAA;'>Nigel:</span> {response}")
        self.is_processing = False
    
    def handle_error(self, error_msg):
        """Handle errors from Gemini API"""
        # Remove "thinking" message
        text = self.conversation.toPlainText()
        text = text.replace("Nigel is thinking...", "")
        self.conversation.setPlainText(text)
        
        # Add error message
        self.conversation.append(f"<span style='color: red;'>Error:</span> {error_msg}")
        self.is_processing = False

    def position_window(self, tray_icon_geometry):
        """Position the window above the tray icon"""
        screen_geometry = QGuiApplication.primaryScreen().geometry()
        x = tray_icon_geometry.x() + tray_icon_geometry.width() // 2 - self.width() // 2
        y = tray_icon_geometry.y() - self.height()
        
        # Ensure window is fully visible on screen
        if x < 0:
            x = 0
        if x + self.width() > screen_geometry.width():
            x = screen_geometry.width() - self.width()
        if y < 0:
            y = 0
        
        self.move(x, y)

class NiGELApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.setQuitOnLastWindowClosed(False)
        
        # Create the system tray icon
        self.tray_icon = QSystemTrayIcon()
        icon_path = get_icon_path("nigel.png")
        
        # If icon doesn't exist, create a simple one
        if not os.path.exists(icon_path):
            import tempfile

            from PIL import Image, ImageDraw

            # Create a temporary icon file
            icon_size = 64
            image = Image.new('RGBA', (icon_size, icon_size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            
            # Make a more visible icon - a filled circle
            draw.ellipse((10, 10, 54, 54), fill="black")
            draw.ellipse((15, 15, 49, 49), fill="white")
            draw.   ellipse((20, 20, 44, 44), fill="blue")
            
            # Save temporary icon
            image.save(icon_path)
        
        self.tray_icon.setIcon(QIcon(icon_path))
        self.tray_icon.setToolTip("NiGEL AI Assistant")
        
        # Create the dropdown window
        self.dropdown = NiGELDropdown()
        
        # Set up tray icon menu
        tray_menu = QMenu()
        
        open_action = QAction("Ask Nigel", self)
        open_action.triggered.connect(self.show_dropdown)
        
        quit_action = QAction("Exit", self)
        quit_action.triggered.connect(self.quit)
        
        tray_menu.addAction(open_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        
        # Show the tray icon
        self.tray_icon.show()
    
    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show_dropdown()
    
    def show_dropdown(self):
        if self.dropdown.isVisible():
            self.dropdown.hide()
        else:
            # Position the dropdown above the tray icon
            tray_geometry = self.tray_icon.geometry()
            self.dropdown.position_window(tray_geometry)
            self.dropdown.show()
            self.dropdown.activateWindow()

if __name__ == "__main__":
    app = NiGELApp(sys.argv)
    sys.exit(app.exec())