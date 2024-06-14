Gsearcher - by frank38

Free to use and modify.

This is a program for searching text in files.
It is written in Python (vers. 3.5, it might work with older versions) 
and Gtk3 libraries. Python3-magic and optionally exiftool for metadata 
are needed.

The extractors are all plugins, that means new ones can be created and 
added. At the moment, the following plugins are present: etext.py for 
text files, epdf.py (requires pdftotext) for pdf files, eodt.py for Libreoffice doc files 
and edoc.py for MS doc files and edocx.py for MS docx files (all of them require libreoffice, but old versions using old more simple programs are in the folder extractors/disabled/OLD).

Note about the pdf files: only searchble pdf files can be indexed, so encrypter and not searcheble ones will be skipped, or will be stored malformed.

The program can also handle multiple databases.

The logs help user to check which files have been indexed, which not and the reason.
The searched words are set in bold.

Internally, the sqlite3 python module is used for storing the data.
