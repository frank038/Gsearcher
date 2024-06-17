#!/usr/bin/env python3

import sqlite3
import subprocess
import os
import sys
import glob
import magic
import importlib
from pathlib import Path
from time import sleep, gmtime, strftime, time

from cfg import USE_MBOX_FILES
if USE_MBOX_FILES == 1:
    import mailbox

class vvar:
    def __init__(self):
        # how many files have been processed
        self.ii = 0
        # how many files have been added
        self.iii = 0
        # how many files have been deleted
        self.iiii = 0
        # how many files have been discharged
        self.iiiii = 0
        # folders not in place
        self.FFOLDER_NOT = 0
        # folders and files issues during indexing
        self.iiiiii = 0
        # metadata
        self.METADATA = ""
        # special tag1
        self.TAG1=""
        # list of files ready to be indexed, only name
        self.list_file = []
        # list of processed files with path
        self.pfiles = []
        # lfolder - folders to get indexed with absolute path
        self.lfolder = []
        # lffolder - folders to get indexed with absolute path
        self.lffolder = []
        # date and time
        self.ddatettime = strftime("%Y %b %d %H:%M:%S", gmtime())
        # where to store the extractor plugins
        self.ePlugins = []
        # # imported modules 
        # self.extractor_objmodule = []
        # the mimetype of each module as they are loaded
        self.extractor_mimmodule = []
        # list of extractors
        self.extractors = []

        # connecting to the database
        self.con = sqlite3.connect('./DATABASE/default.db')
        self.cur = self.con.cursor()
        # the dir of the main program
        main_dir = os.getcwd()
        # create or populate the log files
        os.chdir("LOG")
        self.flog = open("log","a")
        self.flogd = open("file_discharged.log","a")
        self.flogadd = open("file_added.log","a")
        os.chdir(main_dir)
        # import the extractor plugins
        sys.path.append(main_dir+'/'+'extractors/')
        module_dir = "extractors/"
        #
        os.chdir(module_dir)
        #
        self.ePlugins = glob.glob('*.py')
        #
        #aa = 0
        #for asd in self.ePlugins:
        for _i,_comm in enumerate(self.ePlugins):
            #mmodule = os.path.splitext(self.ePlugins[aa])[0]
            mmodule = os.path.splitext(_comm)[0]
            try:
                ee = importlib.import_module(mmodule)
                # self.extractor_objmodule.append(ee)
                self.extractor_mimmodule.append(ee.docType)
                self.extractors.append([ee,ee.docType])
            except ImportError as ioe:
                self.flog.write("{} Module {} failed to be imported.".format(self.ddatettime, ee))
            #aa += 1
        #
        os.chdir(main_dir)
        #
        # import the xml module
        try:
            import xml.etree.cElementTree as ET
        except ImportError:
            import xml.etree.ElementTree as ET
    
        CONFIG_XML = "./DATABASE/config.xml"
        tree = ET.parse(CONFIG_XML)
        root = tree.getroot()
        
        # poputale the folder from the config file
        for isfolder in root.iter('item'):
            if list(isfolder.attrib.values())[0] == 'Folder':
                self.lfolder.append(isfolder.text)
    
    # creates the list of files to be indexed
    def execute_indexing(self, folder_to_index):
        if (Path(folder_to_index).exists() == True) and (os.access(folder_to_index, os.R_OK) == True):
            os.chdir(folder_to_index)
            self.list_file = glob.glob("*")
            llist_file = self.list_file[:]
            mmbox_file = []
            for ffile in self.list_file:
                sleep(0.1)
                if not os.path.isfile(ffile):
                    llist_file.remove(ffile)
                    continue
                _temp_iiiii = self.iiiii
                try:
                    pathfile = folder_to_index+"/"+ffile
                    if (Path(folder_to_index).exists()) and (os.access(pathfile, os.R_OK)):
                        file_magic = magic.detect_from_filename(ffile)[0]
                        if USE_MBOX_FILES == 1:
                            # detect mbox file
                            if file_magic in ["text/plain","text/html"]:
                                ret = self.mbox_detect(ffile)
                                if ret == 1:
                                    mmbox_file.append(ffile)
                                    llist_file = []
                                    continue
                        #
                        self.ii += 1
                        self.pfiles.append(folder_to_index+"/"+ffile)
                        #
                        _is_found = 0
                        for el in self.extractor_mimmodule:
                            if file_magic in el:
                                _is_found = 1
                                break
                        #
                        if _is_found == 0:
                            llist_file.remove(ffile)
                            self.flogd.write("{} File discharged for wrong mimetype: {} in {}\n".format(self.ddatettime, ffile, folder_to_index))
                            self.iiiii += 1
                        #
                        else:
                            mmtime = os.stat(ffile).st_mtime
                            self.cur.execute("""select mtime from tabella where name=(?) and dir=(?)""", (ffile, folder_to_index))
                            mtcontent = self.cur.fetchone()
                            if mtcontent == None:
                                fmtime = 0
                            else:
                                fmtime = mtcontent[0]
                            if mmtime == fmtime:
                                llist_file.remove(ffile)
                            elif fmtime == 0:
                                pass
                            elif mmtime > fmtime:
                                self.cur.execute("""delete from tabella where name=(?) and dir=(?)""", (ffile,folder_to_index))
                                self.con.commit()
                                self.flog.write("{} File updated: {} in {}\n".format(self.ddatettime, ffile, folder_to_index))
                    else:
                        llist_file.remove(ffile)
                        self.flogd.write("{} File discharged for issue during indexing: {} in {}\n".format(self.ddatettime, ffile, folder_to_index))
                        self.iiiiii += 1
                except Exception as E:
                    self.flogd.write("{} File discharged: {} in {} - Reason: {}\n".format(self.ddatettime, ffile, folder_to_index, str(E)))
                    self.iiiii = _temp_iiiii+1
        else:
            self.FFOLDER_NOT += 1
            flog.write("{} Folder issue during indexing: {}\n".format(self.ddatettime, folder_to_index))
            self.iiiiii += 1
        #
        return llist_file,mmbox_file
    
    # the name of all files stored
    def all_name_file(self):
        cname = []
        self.cur.execute("select name,dir from tabella")
        cname1 = self.cur.fetchall()
        for aa in cname1:
            cname.append(aa[1]+"/"+aa[0])
        return cname
    
    # checks if folders exist
    def check_ffolder(self):
        for ffolder in self.lfolder:
            if os.access(ffolder, os.R_OK) is not True:
                self.FFOLDER_NOT += 1
                self.flog.write("{} Folder not accessible: {}\n".format(self.ddatettime, ffolder))
            elif Path(ffolder).exists() == True:
                self.lffolder.append(ffolder)
            else:
                self.FFOLDER_NOT += 1
                self.flog.write("{} Folder not found: {}\n".format(self.ddatettime, ffolder))
    
    # detect mbox file
    def mbox_detect(self, ffile):
        _mbox = mailbox.mbox(ffile)
        # no items means no messages or wrong file type
        if len(_mbox.items()) == 0:
            _mbox.close()
            return 0
        else:
            return 1
    
    # check the mbox file for new emails
    def _mailbox(self, ffile):
        # main_dir = os.getcwd()
        ux_time = str(time())
        folder_to_index = os.path.dirname(os.path.realpath(ffile))
        # single email in mbox file
        m_file_in_mbox = []
        # the email in the database
        m_file_in_db = []
        self.cur.execute("""select name from tabella""")
        m_names = self.cur.fetchall()
        if m_names:
            for ell in m_names:
                m_file_in_db.append(ell[0])
        # list of tuple
        rae = self.cur.fetchmany()
        #
        _mbox = mailbox.mbox(ffile)
        #
        for _mitem in _mbox.items():
            message = _mitem[1]
            if message['date']:
                m_date = str(message['date'])
            else:
                # m_date = ux_time
                m_date = "unknown"
            if message['from']:
                m_from = str(message['from'])
            else:
                m_from = "Unknown"
            # if message['subject']:
                # m_subj = str(message['subject'])
            # else:
                # m_subj = "None"
            #
            stext = m_date+" - "+m_from
            self.cur.execute("""select name from tabella where name=(?)""", (stext,))
            # list of tuple
            rae = self.cur.fetchmany()
            # rae = self.cur.fetchall()
            # rae = self.cur.fetchone()
            #
            m_file_in_mbox.append(stext)
            if stext not in m_file_in_db:
                #m_file_in_mbox.append(stext)
                try:
                    os.unlink("/tmp/123456789")
                except:
                    pass
                _mbox_add = mailbox.mbox("/tmp/123456789")
                _mbox_add.add(message.as_string())
                for ell in self.extractors:
                    if ell[0].fidentify == "mbox":
                        obj = ell[0]
                        break
                freturn = obj.ffile_content("/tmp/123456789")
                # 
                if freturn == False:
                    self.flogd.write("{} File discharged for no content: {} in {}\n".format(self.ddatettime, fti, folder_to_index))
                    self.iiiii += 1
                else:
                    self.iii += 1
                    fti = stext
                    fmime = "application/mbox"
                    # mmtime = os.stat(ffile).st_mtime
                    mmtime = str(time())
                    self.METADATA = freturn[0]
                    ccontent = freturn[1]
                    self.TAG1 = freturn[2]
                    # fti, fmime, mmtime, folder_to_index, ccontent, self.METADATA, self.TAG1
                    self.cur.execute("""insert into tabella (name, mime, mtime, dir, content, metadata, tag1) values (?,?,?,?,?,?,?)""", (fti, fmime, mmtime, folder_to_index, ccontent, self.METADATA, self.TAG1))
                    self.con.commit()
                    self.flogadd.write("{} File added: {} in {}\n".format(self.ddatettime, fti, folder_to_index))
        #
        if m_file_in_mbox:
            for _ff in m_file_in_db:
                if _ff not in m_file_in_mbox:
                    self.cur.execute("""delete from tabella where name=(?)""", (_ff, ))
                    self.con.commit()
                    self.flog.write("{} File deleted from database because the folder doesn't exist anymore': {} in {}\n".format(self.ddatettime, _ff, folder_to_index))
        #
        _mbox.close()
    
    
    def ins_db(self):
        self.check_ffolder()
        for folder_to_index in self.lffolder:
            #
            flist_file,fmbox_file = self.execute_indexing(folder_to_index)
            if flist_file != []:
                for fti in flist_file:
                    mmtime = os.stat(fti).st_mtime
                    fmime = magic.detect_from_filename(fti)[0]
                    #nmod = self.extractor_mimmodule.index(fmime)
                    # obj = self.extractor_objmodule[nmod]
                    obj = None
                    #
                    for ell in self.extractors:
                        if fmime in ell[1] and ell[0].fidentify != "mbox":
                            obj = ell[0]
                            break
                    # maybe redundant
                    if obj == None:
                        self.flogd.write("{} File discharged for no content: {} in {}\n".format(self.ddatettime, fti, folder_to_index))
                        self.iiiii += 1
                        return
                    #
                    freturn = obj.ffile_content(folder_to_index+"/"+fti)
                    if freturn == False:
                        self.flogd.write("{} File discharged for no content: {} in {}\n".format(self.ddatettime, fti, folder_to_index))
                        self.iiiii += 1
                        pass
                    else:
                        self.iii += 1
                        self.METADATA = freturn[0]
                        ccontent = freturn[1]
                        self.TAG1 = freturn[2]
                        self.cur.execute("""insert into tabella (name, mime, mtime, dir, content, metadata, tag1) values (?,?,?,?,?,?,?)""", (fti, fmime, mmtime, folder_to_index, ccontent, self.METADATA, self.TAG1))
                        self.con.commit()
                        self.flogadd.write("{} File added: {} in {}\n".format(self.ddatettime, fti, folder_to_index))
                # delete deleted files
                self.delete_notfile_row()
            #
            if fmbox_file != []:
                for mfile in fmbox_file:
                    self._mailbox(mfile)
    
    
    # deletes the related row if file is accessible no more
    def delete_notfile_row(self):
        cname = self.all_name_file()
        for fname in cname:
            if fname not in self.pfiles:
                self.iiii += 1
                (rfolder_to_index, rfile) = os.path.split(fname)
                self.cur.execute("""delete from tabella where name=(?) and dir=(?)""", (rfile, rfolder_to_index))
                self.con.commit()
                self.flog.write("{} File deleted from database because the folder doesn't exist anymore': {} in {}\n".format(self.ddatettime, rfile, rfolder_to_index))
        
    # return to the main program some data
    def return_file(self):
        llist = "{} {} {} {} {} {}".format(self.ii, self.iii, self.iiii, self.iiiii, self.FFOLDER_NOT, self.iiiiii)
        # close everything
        self.flog.close()
        self.flogd.close()
        self.flogadd.close()
        self.con.commit()
        self.cur.close()
        self.con.close()
        return llist
    
    def _index(self):
        self.ins_db()
        # self.delete_notfile_row()
        aaa = self.return_file()
        print(aaa)

app = vvar()   
app._index()
