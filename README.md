Gsearcher - by frank38

V 1.0.2

This is a program for searching text in files.
It is written in Python (vers. 3.5, it might work with older versions) 
and Gtk3 libraries. Python3-magic and optionally exiftool for metadata 
are needed.
The extractors are all plugins, that means new ones can be created and 
added. At the moment, the following plugins are present: etext.py for 
text files, epdf.py (requires pdftotext) for pdf files, eodt.py (requires odt2txt) 
for Libreoffice doc files, edoc.py (requires catdoc) for MS doc files, 
edocx.py (requires docx2txt) for MS docx files.
The program can also handle multiple databases.
The logs help user to check which files have been indexed, which not and the reason.
