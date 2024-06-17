#!/usr/bin/env python3

import os
# import subprocess
from html.parser import HTMLParser
import html
import mailbox
import glob
import importlib

# name of the module
nameModule = 'embox'
# mimetype handled
docType = ['application/mbox','text/plain','text/html']
# command execute - TRUE meand its an internal procedure
command_execute = "TRUE"
# how to identify the file
fidentify="mbox"
# file metadata
metadata1 = ""
# special tags
tag1=""
# name of the module and file type
hhendler = (nameModule,docType)
# the module return: metadata, content, special tag
ereturn = ()

def nametype_Module():
    return hhendler

# if the attachments are in the following groups, they will be skipped from indexing process
_skip_family_mimetype = ["image","video"]

# if 1 also the attachments will be indexed, otherwise 0
INDEX_ATTACHMENTS = 1

module_dir = os.getcwd()
#main_dir = os.getcwd()

class mailIdexer:
    def __init__(self, _type,_data):
        self._type = _type
        self._data = _data
        self.ePlugins = []
        self.extractors = []
        #
        #main_dir = os.getcwd()
        #module_dir = "extractors"
        #module_dir = "."
        os.chdir(module_dir)
        #
        self.ePlugins = glob.glob('*.py')
        #os.chdir(main_dir)
        #
        for _comm in self.ePlugins:
            # if _comm == "embox.py":
                # continue
            mmodule = _comm.split(".")[0]
            try:
                #ee = importlib.import_module(module_dir+mmodule)
                ee = importlib.import_module(mmodule)
                self.extractors.append(ee)
            except ImportError as ioe:
                self.flog.write("{} Module {} failed to be imported.".format(self.ddatettime, ee))
                pass
        #
        # os.chdir(main_dir)
        
    def _get_content(self):
        ret = False
        for ee in self.extractors:
            if self._type in ee.docType:
                ret = ee.ffile_content(self._data)
                break
        #
        return ret,self._type


class HTMLContent(HTMLParser):
    text = ""
    def handle_data(self, data):
        self.text += html.unescape(data)


def _mailbox(mbox_file):
    _mbox = mailbox.mbox(mbox_file)
    _mtext = ""
    #_mitem = _mbox.items()[0]
    for _mitem in _mbox.items():
    #if _mitem:
        message = _mitem[1]
        metadata1 = "Email : "+message['from']+" - "+message['date']+"\nDate  : "+message['date']+"\nFrom  : "+message['from']+"\nObject: "+message['subject']
        #
        if message.is_multipart():
            for part in message.get_payload():
                if part.get_content_type() == "text/html":
                    try:
                        _data = part.get_payload(decode=True).decode()
                        parser = HTMLContent()
                        parser.feed(_data)
                        _mtext += parser.text
                        parser.close()
                    except:
                        pass
                #
                elif part.get_content_type() == "text/plain":
                    _mtext += part.get_payload(decode=True).decode()
                #
                else:
                    if INDEX_ATTACHMENTS == 1:
                        if part.get_content_type().split("/")[0] in _skip_family_mimetype:
                            continue
                        with open("/tmp/mail_attachment", "bw") as _f:
                            _f.write(part.get_payload(decode=True))
                        MI = mailIdexer(part.get_content_type(),"/tmp/mail_attachment")
                        # tuple: metadata - content
                        _data,_type = MI._get_content()
                        if _data != False:
                            _mtext += "\n\nAttachment type: "+_type+"\n\n"
                            _mtext += _data[0]
                            _mtext += _data[1]
                        # os.unlink("/tmp/mail_attachment")
        else:
            try:
                _data = message.get_payload(decode=True).decode()
                parser = HTMLContent()
                parser.feed(_data)
                _mtext += parser.text
                parser.close()
            except:
                _mtext += message.get_payload(decode=True).decode()
    #
    return metadata1,_mtext


#if False is returned then no text has been extract
def ffile_content(ffile):
    try:
        metadata1,ctext = _mailbox(ffile)
        #
        if len(ctext) > 0:
            ereturn = (metadata1, ctext, tag1)
            return ereturn
        else:
            return False
    except:
        return False

