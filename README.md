Gsearcher

Free to use and modify.

Requirements:
- python3
- gtk3 binding
- xdg-open (to open the files searched by double clicking on it)

This is a program for searching text in files. It is also a simple frontend to the console program find for searching files by name or by modification time or by access time.
It is written in Python3 and Gtk3 libraries. Python3-magic and optionally exiftool for metadata 
are needed.

The extractors are all plugins, that means new ones can be created and 
added easily. The following plugins are included: etext.py for 
text files, epdf.py (requires pdftotext) for pdf files, eodt.py for Libreoffice doc files and edoc.py for MS doc files and edocx.py for MS docx files (all of them require libreoffice, but old versions using old more simple programs are in the folder extractors/disabled/OLD), ehtml for html files, eimap for imap and mbox email files (only if each email is in a separate file; attachments will be indexed too, unless this option is disable in the module). If the program for extracting the text is not present in your system (except for those using an internal procedure), the plugin using that program will be disabled automatically.

The cfg.py is the config file for the program.

About the indexers: only searchable pdf files can be indexed, so encrypter and not searcheble ones will be skipped, or will be stored malformed; the text extracted from the files by the extractors depends on the ability of them to extract it.

Experimentally, emails in regular mbox and imap format can be indexed, and its attachments (e.g. pdf and text files) as well (the same extractors for other regular files will be used). While there is not any reasons to avoid indexing in the same database mbox files and other type of files, it is better to use a dedicated database for emails. How the mbox indexing works: after choosing the folder containing the mbox files (it is better to work with copy of them to be safe), start the indexing process from the menu; each emails will be stored as separate data. After every indexing process, new emails will be added, and deleted email by the user will be deleted from the database too.

The program can also handle multiple databases.

The logs help user to check which files have been indexed, which not and the reason.
The searched words are set in bold.

Internally, the sqlite3 python module is used for storing the data.

The program can be directly executed if its exec flag is set. 
The first time you will be asked to create - and choose - a 
new database. The next step is to choose which folder/s the program 
will search for files.
In the configuration window, the second tab shows the extractors 
enabled, the extractors disabled and the reasons, mainly for 
'not command found'.

![My image](https://github.com/frank038/Gsearcher/blob/master/Screenshot3.png)

![My image](https://github.com/frank038/Gsearcher/blob/master/Screenshot1.png)

![My image](https://github.com/frank038/Gsearcher/blob/master/Screenshot2.png)
