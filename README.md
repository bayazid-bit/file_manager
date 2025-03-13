# File Manager

A **PyQt5-based File Manager** with support for **local and remote file browsing**. It provides a simple and intuitive **GUI** for managing files and directories.

## Features

✅ **GUI-based File Browser** using PyQt5  
✅ **Sidebar with Quick Access** (Home, Documents, Downloads, etc.)  
✅ **Navigation Controls** (Back, Forward, Refresh, Address Bar)  
✅ **Show/Hide Hidden Files**  
✅ **Remote Server Connection** via HTTP  
✅ **File and Folder Grid View with Icons**  
✅ **Open Local Files with System Default Apps**  
✅ **Download Files from Remote Servers**  

## Installation

```bash
# Clone the repository
git clone https://github.com/bayazid-bit/file_manager.git
cd file_manager

# Install dependencies
pip install -r requirements.txt

# Run the application
python file_manager.py
```

## Dependencies

Make sure you have **Python 3.x** installed, then install the required dependencies:

```bash
pip install PyQt5 requests beautifulsoup4
```

## Usage

Run the script to open the file manager GUI:

```bash
python file_manager.py
```

### Connecting to a Remote Server
1. Click **"Connect to Remote"** in the sidebar.
2. Enter the remote server address (e.g., `http://192.168.1.100:8000`).
3. Browse and download files from the remote server.

### Navigating Directories
- Use **Back**, **Forward**, and **Refresh** buttons for easy navigation.
- Click on folders to open them.
- Use the **address bar** to enter a path manually.
- Click **"Show Hidden Files"** to toggle hidden files visibility.



## Future Improvements
- ✅ **Add File Operations** (Copy, Move, Rename, Delete)
- ✅ **Support for FTP/SFTP Connections**
- ✅ **Drag & Drop Support for File Transfers**
- ✅ **Multi-tab Interface**

## License
This project is licensed under the **MIT License**.

## Contributing
Pull requests are welcome! Feel free to submit issues and suggest features.

## Author
Bayazid (https://github.com/bayazid-bit)

