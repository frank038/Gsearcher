Gsearcher - by frank38

V 1.0.2

This python3 program is executed by launching the file Gsearcher.py. 
It is a python3 (vers. 3.5, it might work with older versions) 
program using the Gtk3 toolkit. 
The program can be directly executed if its exec flag is set. 
The first time you will be asked to create - and choose - a 
new database. The next step is to choose which folder/s the program 
will search for files.
In the configuration window, the second tab shows the extractors 
enabled, the extractors disabled and the reasons, mainly for 
'not command found'.
-------
How to change the window size of the main program:
at lines 29 and 31 change the numbers 1100 (width) and 
800 (height) to whatever you want.

After every query, the program opens 10 preview tabs at most.
This limit can be changed by setting a different value 
at line 215 of the main program. A value is required.

Programs and modules required:
python3
Gtk3 libs and the python3 modules (gir) 
python3-magic
exiftool (for metadata, optional)
