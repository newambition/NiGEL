# Dependencies

This document lists the project's dependencies and their roles.

## Core Dependencies

These dependencies are essential for the application to run.

*   **PyQt6:** A comprehensive set of Python bindings for Qt v6. It is used to create the application's graphical user interface (GUI).
*   **Pillow:** The Python Imaging Library, used for opening, manipulating, and saving many different image file formats. In this project, it is used to handle the `nigel.png` icon.
*   **google-generativeai:** The official Python library for the Google Gemini API. It is used to interact with the generative AI model that powers the conversation.

## Build Dependencies

These dependencies are used for packaging the application into a standalone executable.

*   **PyInstaller:** A tool that freezes (packages) Python applications into stand-alone executables, under Windows, GNU/Linux, Mac OS X, FreeBSD, Solaris and AIX.
*   **auto-py-to-exe:** A graphical interface for PyInstaller. It is used to simplify the process of building the executable.

## Development Dependencies

These dependencies are used for managing the development environment.

*   **Poetry:** A tool for dependency management and packaging in Python. It is used to manage the project's dependencies and to build the application.
