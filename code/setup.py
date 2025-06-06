from cx_Freeze import setup, Executable
import os

executables = [
    Executable("main.py", target_name="RAMsey")
]

# Locate the PyQt6 Qt6 directory
pyqt6_path = os.path.join(os.path.dirname(__file__), "path/to/venv/lib/python3.13/site-packages/PyQt6/Qt6")

build_exe_options = {
    "packages": ["os", "sys", "random", "math", "tkinter", "PyQt6", "weakref"],
    "include_files": [
        "images/",  # Include the images folder
        os.path.join(pyqt6_path, "lib"),  # Include the Qt6 libraries
        os.path.join(pyqt6_path, "plugins"),  # Include the Qt6 plugins
    ],
    "excludes": [
        "libpq",
        "psycopg2",
        "sqlite3",
        "email",
        "http",
        "xml",
        "unittest",
        "logging",
        "asyncio",
        "distutils",
        "multiprocessing.dummy",
        "pydoc",
        "test",
        "bz2",
        "lzma",
        "lib2to3",
    ],
}

setup(
    name="RAMsey",
    version="1.0",
    description="RAMsey Desktop App",
    options={"build_exe": build_exe_options},
    executables=executables
)