#!/usr/bin/env python3

import os
import subprocess

# name of the module
nameModule = 'edocx'
# mimetype handled
docType = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
# command execute
command_execute = "docx2txt"
# how to identify the file
fidentify="Office word docx"
# file metadata
metadata1 = ""
# special tag
tag1=""
# name of the module and file type
hhendler = (nameModule,docType)
# the module return: metadata, content, special tag
ereturn = ()

# tre minuscole prima della maiuscola oppure n_Name
def nametype_Module():
    return hhendler

def ffile_content(ffile):
    try:
        metadata1 = subprocess.check_output(["exiftool", "-FileName", "-Title", "-Subject", "-Keywords", "-Description", "-Pages", "-CreateDate", "-Document", "-FileSize", ffile], universal_newlines=True)
    except:
        metadata1 = ""
    try:
        ctext = subprocess.check_output(["docx2txt", ffile, "-"], universal_newlines=True)
        if len(ctext) > 0:
            ereturn = (metadata1, ctext, tag1)
            return ereturn
        else:
            return False
    except:
        return False
