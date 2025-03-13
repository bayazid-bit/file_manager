import os
import sys
import requests
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    
    QHBoxLayout,
    QLineEdit,
    
    QPushButton,
    QMessageBox,
    
    QGridLayout,
    
    QLabel,
    
    QScrollArea,
    QListWidget,
    QListWidgetItem,
    QInputDialog,
)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt


class FileBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Browser")
        self.setGeometry(100, 100, 1000, 600)

        
        self.history = []
        self.current_index = -1

        
        self.show_hidden_files = False

       
        self.remote_server = None

        
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QHBoxLayout(self.main_widget)  
        

       
        self.add_sidebar()

        
        self.add_main_view()

        
        self.load_directory(os.path.expanduser("~"))

    def add_sidebar(self):
        
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(150)  # Set a fixed width for the sidebar
        self.sidebar.itemClicked.connect(self.on_sidebar_item_clicked)

        
        common_folders = [
            ("Home", os.path.expanduser("~")),
            ("Documents", os.path.expanduser("~/Documents")),
            ("Downloads", os.path.expanduser("~/Downloads")),
            ("Pictures", os.path.expanduser("~/Pictures")),
            ("Music", os.path.expanduser("~/Music")),
            ("Videos", os.path.expanduser("~/Videos")),
        ]

        for name, path in common_folders:
            item = QListWidgetItem(name)
            item.setData(Qt.UserRole, path)  
            self.sidebar.addItem(item)

        
        self.connect_button = QPushButton("Connect to Remote")
        self.connect_button.clicked.connect(self.connect_to_remote)
        
        self.sidebar.addItem(QListWidgetItem())  
        
        self.sidebar.addItem(QListWidgetItem("Remote Connection"))
        
        self.sidebar.setItemWidget(self.sidebar.item(self.sidebar.count() - 1), self.connect_button)

        self.layout.addWidget(self.sidebar)

    def add_main_view(self):
        
        main_view = QWidget()
        main_layout = QVBoxLayout(main_view)

       
        self.address_bar = QLineEdit()
        self.address_bar.returnPressed.connect(self.navigate_to_path)
        main_layout.addWidget(self.address_bar)

        
        self.nav_layout = QHBoxLayout()
        self.back_button = QPushButton()
        self.back_button.setIcon(QIcon.fromTheme("go-previous"))  # System icon for Back
        self.back_button.clicked.connect(self.go_back)
        self.forward_button = QPushButton()
        
        self.forward_button.setIcon(QIcon.fromTheme("go-next"))  # System icon for Forward
        self.forward_button.clicked.connect(self.go_forward)
        self.refresh_button = QPushButton()
        
        self.refresh_button.setIcon(QIcon.fromTheme("view-refresh"))  # System icon for Refresh
        self.refresh_button.clicked.connect(self.refresh)
        self.toggle_hidden_button = QPushButton("Show Hidden Files")
        
        self.toggle_hidden_button.clicked.connect(self.toggle_hidden_files)
        self.nav_layout.addWidget(self.back_button)
        self.nav_layout.addWidget(self.forward_button)
        
        self.nav_layout.addWidget(self.refresh_button)
        self.nav_layout.addWidget(self.toggle_hidden_button)
        main_layout.addLayout(self.nav_layout)

       
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        
        self.grid_layout = QGridLayout(self.scroll_content)
        
        self.scroll_area.setWidget(self.scroll_content)
        
        main_layout.addWidget(self.scroll_area)

        self.layout.addWidget(main_view)

    def connect_to_remote(self):
        """Connect to a remote file server."""
        server, ok = QInputDialog.getText(
            self, "Connect to Remote", "Enter server address (e.g., http://192.168.1.100:8000):"
        )
        if ok and server:
            self.remote_server = server
            self.load_directory("/")  # Start at the root directory

    def load_directory(self, path):
        
        if self.remote_server:
           
            try:
                url = f"{self.remote_server}{path}"
                response = requests.get(url)
                if response.status_code == 200:
                    files = self.parse_html_directory_listing(response.text)
                    self.display_files(files, path)
                else:
                    QMessageBox.warning(self, "Error", f"Failed to fetch directory: {response.text}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to connect to server: {e}")
        else:
            
            if not os.path.isdir(path):
                QMessageBox.warning(self, "Error", f"Directory not found: {path}")
                return

            
            if self.current_index != len(self.history) - 1:
                self.history = self.history[: self.current_index + 1]
            self.history.append(path)
            self.current_index += 1

            
            self.address_bar.setText(path)

            
            for i in reversed(range(self.grid_layout.count())):
                self.grid_layout.itemAt(i).widget().setParent(None)

            
            if path != os.path.expanduser("~"):
                self.add_item("..", os.path.dirname(path), "folder", 0, 0)
                row, col = 0, 1  
            else:
                row, col = 0, 0

           
            for item in os.listdir(path):
                
                if not self.show_hidden_files and item.startswith("."):
                    continue

                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    self.add_item(item, item_path, "folder", row, col)
                else:
                    file_type = self.get_file_type(item)
                    self.add_item(item, item_path, file_type, row, col)

                
                col += 1
                if col > 5:  
                    col = 0
                    row += 1

    def parse_html_directory_listing(self, html):
        """Parse the HTML directory listing from python -m http.server."""
        soup = BeautifulSoup(html, "html.parser")
        files = []
        for link in soup.find_all("a"):
            href = link.get("href")
            if href and href != "../":  
                files.append({
                    "name": href.rstrip("/"),
                    "is_dir": href.endswith("/"),
                })
        return files

    def display_files(self, files, path):
        
        
        for i in reversed(range(self.grid_layout.count())):
            self.grid_layout.itemAt(i).widget().setParent(None)

        
        self.address_bar.setText(path)

       
        if path != "/":
            self.add_item("..", os.path.dirname(path), "folder", 0, 0)
            row, col = 0, 1  
        else:
            row, col = 0, 0

       
        for item in files:
            item_name = item["name"]
            item_path = os.path.join(path, item_name)
            if item["is_dir"]:
                self.add_item(item_name, item_path, "folder", row, col)
            else:
                file_type = self.get_file_type(item_name)
                self.add_item(item_name, item_path, file_type, row, col)

           
            col += 1
            if col > 5:  
                col = 0
                row += 1

    def add_item(self, name, path, item_type, row, col):
        """Add an item (file or folder) to the grid view."""
        
        item_widget = QWidget()
        item_layout = QVBoxLayout(item_widget)
        item_layout.setAlignment(Qt.AlignCenter)

       
        icon_label = QLabel()
        icon = self.get_system_icon(item_type)
        if icon:
            icon_label.setPixmap(icon.pixmap(64, 64))  
        item_layout.addWidget(icon_label)

        
        text_label = QLabel(name)
        text_label.setAlignment(Qt.AlignCenter)
        item_layout.addWidget(text_label)

        
        self.grid_layout.addWidget(item_widget, row, col)

        
        item_widget.mousePressEvent = lambda event, p=path: self.on_item_clicked(p)

    def get_system_icon(self, item_type):
        """Get system icon based on item type."""
        if item_type == "folder":
            return QIcon.fromTheme("folder")
        elif item_type == "mp3":
            return QIcon.fromTheme("audio-x-generic")
        elif item_type == "mp4":
            return QIcon.fromTheme("video-x-generic")
        elif item_type == "python":
            return QIcon.fromTheme("text-x-python")
        else:
            return QIcon.fromTheme("text-x-generic")  # Fallback for unknown files

    def on_item_clicked(self, path):
        """Handle clicks on items in the grid view."""
        if self.remote_server:
            if path.endswith(".."): 
                path = os.path.dirname(os.path.dirname(path))
            self.load_directory(path)
        else:
            if os.path.isdir(path):
                self.load_directory(path)
            else:
                self.open_file(path)

    def on_sidebar_item_clicked(self, item):
        
        path = item.data(Qt.UserRole)  
        self.load_directory(path)

    def open_file(self, path):
        
        if self.remote_server:
            # Download the file from the remote server
            try:
                url = f"{self.remote_server}{path}"
                response = requests.get(url, stream=True)
                if response.status_code == 200:
                    file_name = os.path.basename(path)
                    with open(file_name, "wb") as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    QMessageBox.information(self, "Download Complete", f"File saved as {file_name}")
                else:
                    QMessageBox.warning(self, "Error", f"Failed to download file: {response.text}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to download file: {e}")
        else:
            
            try:
                if sys.platform == "win32":
                    os.startfile(path)
                elif sys.platform == "darwin":
                    os.system(f"open '{path}'")
                else:
                    os.system(f"xdg-open '{path}'")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Unable to open file: {e}")

    def navigate_to_path(self):
        """Navigate to the path entered in the address bar."""
        path = self.address_bar.text()
        if self.remote_server:
            self.load_directory(path)
        else:
            if os.path.exists(path):
                self.load_directory(path)
            else:
                QMessageBox.warning(self, "Error", f"Path not found: {path}")

    def go_back(self):
        """Go back in the history."""
        if self.current_index > 0:
            self.current_index -= 1
            self.load_directory(self.history[self.current_index])

    def go_forward(self):
        """Go forward in the history."""
        if self.current_index < len(self.history) - 1:
            self.current_index += 1
            self.load_directory(self.history[self.current_index])

    def refresh(self):
        """Refresh the current directory."""
        self.load_directory(self.address_bar.text())

    def toggle_hidden_files(self):
        """Toggle the display of hidden files."""
        self.show_hidden_files = not self.show_hidden_files
        self.toggle_hidden_button.setText(
            "Hide Hidden Files" if self.show_hidden_files else "Show Hidden Files"
        )
        self.refresh()  # Refresh the current directory.

    def get_file_type(self, filename):
        """Determine the file type based on its extension."""
        if filename.endswith(".mp3"):
            return "mp3"
            
        elif filename.endswith(".mp4"):
            return "mp4"
            
        elif filename.endswith(".py"):
            return "python"
            
        else:
            return "unknown"


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    browser = FileBrowser()
    browser.show()
    
    sys.exit(app.exec_())
