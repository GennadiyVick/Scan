# Scan. 
Scan is a program for scanning documents and other images. 

![screenshot](https://github.com/GennadiyVick/Scan/blob/master/image.jpg)
## Required:
To run the program, you need the `PyQt5`, `Pillow` and `sane` modules installed for `Python` version 3.


## Installing.  

### Linux:
For the program to work in Linux, you need to use python version 3 or higher.
Most distributions have `python` preinstalled and you don't need to download and install it, 
you just need to install the `PyQt5`, `Pillow` and `sane` modules.
If you do not have python3 installed, you can install it using your package manager, 
for example, in distributions based on Debian, it is installed like this:
```console
sudo apt-get install python3
```
To install the PyQt5 and Pillow modules in the console enter:
```console
sudo apt-get install python3-pyqt5
pip3 install Pillow
```
to install sane module:
```console
sudo apt install python3-sane
```
The program starts like this:
```console
python3 program_path/scan.py
```
You can also add permission to run the script and double-click to run it, as well as create a desktop shortcut.

### MS Windows:
You can download the distribution from [python.org](https://www.python.org/downloads/) and double-click the installation ,
after installation, you need to install the `PyQt5`, `Pillow` and `sane` modules.
Installing the `sane` module on Windows OS is much more complicated and I have not done it. To compile a module, you need the Visual Studio Professional developer framework version 14 or later. If you have it then you can install it like this:
```console
python -m pip install python-sane
python -m pip install pyqt5
python -m pip install Pillow
```
the program will download and install the module.
To run this program, you must enter in the console
```console
python program_path\scan.py
```
You can also create a launch shortcut on the desktop.
To run from a shortcut, use `pythonw` instead of `python`
```console
pythonw program_path\scan.py
```

Author: Roganov G.V. roganovg@mail.ru


