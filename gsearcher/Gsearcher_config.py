#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, Gio
from gi.repository.GdkPixbuf import Pixbuf
import os
import sys
import glob
import importlib
from pathlib import Path
import shutil
from time import gmtime, strftime, time
# import mailbox
# import magic

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

# name of config file
# CONFIG_XML = "./DATABASE/config.xml"
from cfg import CONFIG_XML
from cfg import USE_MBOX_FILES
# directory del programma
main_dir = os.getcwd()
# directory HOME
homepath = str(Path.home())
# date and time
ddatettime = strftime("%Y %b %d %H:%M:%S", gmtime())

def cr_history():
    if Path(CONFIG_XML).exists() == False:
        print("Config file not found: reinstall the program.")
        sys.exit()
cr_history()

# load the configuration file
tree = ET.parse(CONFIG_XML)
root = tree.getroot()

fdir = "extractors/"
sys.path.append(main_dir+'/'+'extractors/')
sys.path.append(main_dir+'/'+'extractors/disabled/')
# list of plugins in extractors and disabled folders
ePlugins = []
# list of plugins in extractors and disabled folders without .py
eePlugins = []

os.chdir("extractors")
# plugins in extractors
ePlugins1 = glob.glob('*.py')
os.chdir("disabled")
# plugins in extractors/disabled
ePlugins2 = glob.glob('*.py')
# both plugins
ePlugins = ePlugins1 + ePlugins2

for ep in ePlugins:
    ggg = os.path.splitext(ep)[0]
    eePlugins.append(ggg)
os.chdir(main_dir)

# list of commands used by all extractors
extractor_command = []
# list of the filename of the extractors
extractor_filename = []
# list of identify of the extractors
extractor_identify = []

i = 0
for ep in eePlugins:
    try:
        ee = importlib.import_module(ep)
        extractor_filename.append(ePlugins[i])
        extractor_command.append(ee.command_execute)
        extractor_identify.append(ee.fidentify)
        i += 1
    except ImportError as ioe:
        print(ioe)

# search for languages
lang_support = []
elang_support = []
os.chdir("languages")
lang_support = glob.glob('*.py')
if (not "lang.py" in lang_support) or lang_support == []:
    print("Problem with the language files: reinstall the program.")
    sys.exit()
lang_support.remove("lang.py")    
for lang in lang_support:
    elang_support.append(os.path.splitext(lang)[0])
os.chdir(main_dir)

sys.path.append(main_dir+'/'+'languages/')
l = importlib.import_module('lang')

ii = 0
aii = 0

# file manager
not_system_fm = False
file_manager = 'SYSTEM'
try:
    with open("./DATA/FileManager","r") as f:
        FM = f.readline()
        if FM != 'SYSTEM':
            file_manager = FM
            not_system_fm = True
except:
    pass

class MainWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Gsearcher Config")
        self.set_icon_from_file("DATA/icons/gsearcher.svg")
        self.connect("delete-event", Gtk.main_quit)
        self.set_border_width(5)
        self.set_default_size(1024, 800)
        self.set_resizable(True)
        # add grid
        self.grid = Gtk.Grid()
        self.add(self.grid)
        # notebook in grid
        self.notebook = Gtk.Notebook(hexpand=True, vexpand=True)
        self.notebook.set_scrollable(True)
        self.grid.attach(self.notebook, 0,0,1,1)
        # quit button
        self.button_quit = Gtk.Button(label=l.Quit)
        self.button_quit.connect("clicked", self.on_main_quit)
        self.grid.attach(self.button_quit, 0,1,1,1)
        #
        self.page1 = Gtk.Box()
        self.page1.set_border_width(10)
        self.notebook.append_page(self.page1, Gtk.Label(label=l.General))
        self.page2 = Gtk.Box()
        #self.page2.set_border_width(10)
        self.notebook.append_page(self.page2, Gtk.Label(label=l.Extractors))
        self.page3 = Gtk.Box()
        self.page3.set_border_width(10)
        self.notebook.append_page(self.page3, Gtk.Label(label=l.tab_other))
        ###### tab 1
         # vbox1 in tab1
        self.vbox1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.page1.add(self.vbox1)
         # scrolled window in vbox1
        self.scrolledwindow = Gtk.ScrolledWindow()
        self.scrolledwindow.set_hexpand(True)
        self.scrolledwindow.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scrolledwindow.set_placement(Gtk.CornerType.TOP_LEFT)
        self.vbox1.pack_start(self.scrolledwindow, True, True, 0)
         # listbox in scrolled window
        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.listbox.connect("row-activated", self.get_ffolder)
        self.scrolledwindow.add(self.listbox)
        # buttons
         # hboxb in vbox1 after scrolled window
        self.hboxb = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
         # button_add in hboxb
        self.button_add = Gtk.Button(label=l.Add)
        self.button_add.connect("clicked", self.add_ffolder)
        self.hboxb.pack_start(self.button_add, True, True, 0)
         # button_delete in hboxb
        self.button_delete = Gtk.Button(label=l.Delete)
        self.button_delete.connect("clicked", self.del_ffolder)
        self.hboxb.pack_start(self.button_delete, True, True, 0)
        self.vbox1.pack_start(self.hboxb, False, False, 0)
        ####### end tab 1
        ####### tab 2
        # search if each command is in path
        self.lscrolledwindow = Gtk.ScrolledWindow()
        self.lscrolledwindow.set_hexpand(True)
        self.lscrolledwindow.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.lscrolledwindow.set_placement(Gtk.CornerType.TOP_LEFT)
        self.page2.add(self.lscrolledwindow)
        #
        grida = Gtk.Grid()
        grida.set_border_width(20)
        #
        for _idx,ccommand in enumerate(extractor_command):
            if ccommand == "TRUE":
                _comm = "INTERNAL"
            else:
                _comm = shutil.which(ccommand)
            # # alignment1 = Gtk.Alignment()
            # alignment1 = Gtk.Alignment.new(0, 0, 0, 0)
            # alignment1.set_hexpand(True)
            # # alignment1.set(0, 0, 0, 0)
            switch = Gtk.Switch()
            label = Gtk.Label(xalign=0)
            label.set_text("Plugin {}".format(extractor_filename[_idx]))
            # alignment1.add(label)
            labela = Gtk.Label(xalign=0)
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
            # hbox.pack_start(alignment1, False, True, 0)
            hbox.pack_start(label, True, True, 0)
            hbox.pack_start(switch, False, False, 0)
            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
            vbox.pack_start(hbox, True, True, 0)
            vbox.pack_start(labela, True, True, 0)
            separatortab2 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
            vbox.pack_start(separatortab2, False, True, 10)
            grida.attach(vbox, 0,_idx,1,1)
            pplugdis = (extractor_filename[_idx] in ePlugins2)
            if (pplugdis == True) and (_comm == None):
                labela.set_text("The command <b>{}</b> cannot be found.\nThe <b>{}</b> files cannot be indexed.\n(Need restarting)\n\n".format(ccommand, extractor_identify[_idx]))
                labela.set_use_markup(True)
                switch.set_active(False)
            elif pplugdis == True:
                labela.set_text("The command <b>{}</b> has been found.\nThe <b>{}</b> files can be indexed.\n\n".format(ccommand, extractor_identify[_idx]))
                labela.set_use_markup(True)
                switch.set_active(False)
            elif _comm != None:
                if _comm == "INTERNAL":
                    labela.set_text("Internal command.\nThe <b>{}</b> files can be indexed.\n\n".format(extractor_identify[_idx]))
                else:
                    labela.set_text("The command <b>{}</b> has been found.\nThe <b>{}</b> files can be indexed.\n\n".format(ccommand, extractor_identify[_idx]))
                labela.set_use_markup(True)
                switch.set_active(True)
            elif (_comm == None) and (extractor_filename[_idx] not in ePlugins2) :
                labela.set_text("The command <b>{}</b> cannot be found.\nThe <b>{}</b> files cannot be indexed.\n(Need restarting)\n\n".format(ccommand, extractor_identify[_idx]))
                labela.set_use_markup(True)
                switch.set_active(False)
                # move the plugin away
                os.chdir("extractors")
                os.rename(extractor_filename[_idx],"disabled/"+extractor_filename[_idx])
                os.chdir(main_dir)
                # write error in the log file
                flog = open(main_dir+"/LOG/log","a")
                flog.write("{} The command {} cannot be found. The plugin {} has been disabled. The {} files cannot be indexed.\n".format(ddatettime,ccommand, extractor_filename[_idx], extractor_identify[_idx]))
                flog.close()
            switch.connect("notify::active", self.activate_cb, _comm, extractor_filename[_idx])
            #
        self.lscrolledwindow.add(grida)
        ####### end tab 2
        ####### tab 3
        vbox3 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        self.page3.add(vbox3)
        # language section
        # # alignment2 = Gtk.Alignment()
        # alignment2 = Gtk.Alignment.new(0, 0, 0, 0)
        # alignment2.set_hexpand(True)
        # # alignment2.set(0, 0, 0, 0)
        hbox3a = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        label3a = Gtk.Label(label=l.Choose_the_language)
        # alignment2.add(label3a)
        # hbox3a.pack_start(alignment2, False, False, 0)
        hbox3a.pack_start(label3a, True, False, 0)
        liststore3a = Gtk.ListStore(str)
        for llang in range(len(elang_support)):
            liststore3a.append([elang_support[llang]])
        self.combo_search3a = Gtk.ComboBox()
        self.combo_search3a.set_model(liststore3a)
        self.combo_search3a.set_active(0)
        self.cellrenderertext = Gtk.CellRendererText()
        self.combo_search3a.pack_start(self.cellrenderertext, True)
        self.combo_search3a.add_attribute(self.cellrenderertext, "text", 0)
        hbox3a.pack_start(self.combo_search3a, True, True, 0)
        button3a = Gtk.Button(label=l.Select)
        button3a.connect("clicked", self.on_language_changed)
        hbox3a.pack_start(button3a, True, True, 0)
        #
        vbox3.pack_start(hbox3a, False, False, 0)
        # separator
        separator1 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        vbox3.pack_start(separator1, False, False, 0)
        # file manager
        self.hbox100 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        checkbutton100 = Gtk.CheckButton(label=l.UseDefaultFM)
        vbox3.pack_start(checkbutton100, False, False, 0)
        self.label100 = Gtk.Label(label=l.OrUse, xalign=0)
        self.label100.set_sensitive(not_system_fm)
        self.hbox100.pack_start(self.label100, False, False, 0)
        self.entry100 = Gtk.Entry()
        self.entry100.set_sensitive(not_system_fm)
        self.hbox100.pack_start(self.entry100, True, True, 0)
        self.button100 = Gtk.Button(label=l.Select)
        self.button100.set_sensitive(not_system_fm)
        self.button100.connect("clicked", self.on_filemanager_changed)
        vbox3.pack_start(self.hbox100, False, False, 0)
        vbox3.pack_start(self.button100, False, False, 0)
        # file manager
        if file_manager == 'SYSTEM':
            checkbutton100.set_active(True)
        else:
            checkbutton100.set_active(False)
            self.label100.set_sensitive(True)
            self.button100.set_sensitive(True)
            self.entry100.set_sensitive(True)
            self.entry100.set_text(FM)
        #
        checkbutton100.connect("toggled", self.on_check_button_toggled)
        # separator
        separator2 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        vbox3.pack_start(separator2, False, False, 0)
        self.button_dellog = Gtk.Button(label=l.DeleteLog)
        self.button_dellog.connect("clicked", self.on_dellog)
        vbox3.pack_start(self.button_dellog, False, False, 0)
        separator3 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        vbox3.pack_start(separator3, False, False, 0)
        ####### end tab 3
        
        # populate the listbox at startup from config.xml
        # for existing folders
        aa = []
        # for non-existing folders
        bb = []
        # populate de list aa
        for iitem in root.iter('item'):
            if list(iitem.attrib.values())[0] == 'Folder':
                ttext = iitem.text
                aa.append(ttext)
        # delete the folders which are not in place
        # from listbox and config.xml
        fnp = 0
        for folder_not in aa[:]:
            if os.path.exists(folder_not) == False:
                fnp += 1
                aa.remove(folder_not)
                bb.append(folder_not)
                for iitem in root.iter('item'):
                    if folder_not == iitem.text:
                        root.remove(iitem)
                        tree = ET.ElementTree(root)
                        tree.write(CONFIG_XML)
        if fnp > 0:
            self.folder_not_place()
            ddatetime = strftime("%Y %b %d %H:%M:%S", gmtime())
            try:
                flog=open(main_dir+"/LOG/log","a")
                for bf in bb:
                    flog.write("{} Folder {} cannot be found.\n".format(ddatetime, bf))
                fclose()
            except:
                pass
        else:
            pass
                
        # populate the listbox
        for iitem in aa:
            row = Gtk.ListBoxRow()
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
            label = Gtk.Label(xalign=0)
            label.set_single_line_mode(True)
            label.set_text("{}".format(iitem))
            hbox.pack_start(label, True, True, 0)
            row.add(hbox)
            self.listbox.add(row)

######## tab 1
    # quit and open the mainwindow 
    def on_main_quit(self, widget):
        os.execl("./Gsearcher.py","&")
        Gtk.main_quit
    
    # check folders are in place
    def folder_not_place(self):
        message1 = l.MessageT1
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
            Gtk.ButtonsType.OK, "")
        dialog.format_secondary_text(message1)
        dialog.run()
        dialog.destroy()
    
    # add the chosen folders
    def add_ffolder(self, widget):
        ffolder = None
        # do not add folder already in list
        folder_in_list = []
        for ffold in root.findall('item'):
            folder_in_list.append(ffold.text)
        filechooserdialog = Gtk.FileChooserDialog(l.ChooseFolder, self,Gtk.FileChooserAction.SELECT_FOLDER)
        filechooserdialog.set_default_size(800, 400)
        filechooserdialog.add_button(l.AddFolder, Gtk.ResponseType.OK)
        filechooserdialog.set_current_folder(str(Path.home()))
        #
        response = filechooserdialog.run()
        if response == Gtk.ResponseType.OK:
            ffolder = filechooserdialog.get_filename()
            if ffolder not in folder_in_list:
                child = ET.Element('item', kind="Folder")
                root.append(child)
                child.text = ffolder
                tree = ET.ElementTree(root)
                tree.write(CONFIG_XML)
                #
                row = Gtk.ListBoxRow()
                hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
                label = Gtk.Label(xalign=0)
                label.set_single_line_mode(True)
                label.set_text("{}".format(ffolder))
                hbox.pack_start(label, True, True, 0)
                row.add(hbox)
                self.listbox.add(row)
                label.show()
                hbox.show()
                row.show()
                self.listbox.show()
        #
        filechooserdialog.destroy()
        #
        # if USE_MBOX_FILES == 1:
            # self._check_mbox(ffolder)
        
    # def _check_mbox(self, _folder):
        # _list_items = os.listdir(_folder)
        # #
        # for el in _list_items:
            # ffile = os.path.join(_folder,el)
            # if not os.path.isfile(ffile):
                # continue
            # # needs improvements on detection without any extension
            # fmime = magic.detect_from_filename(ffile)[0]
            # # a mbox file can be detected as text file
            # if fmime in ["application/mbox","text/plain","text/html"]:
                # self._mailbox(ffile)
            
    # # create the dir MAIL and the file mbox_folders
    # def _mailbox(self, ffile):
        # _mbox = mailbox.mbox(ffile)
        # # no items means no messages or wrong file type
        # if len(_mbox.items()) == 0:
            # _mbox.close()
            # return
        # #
        # _parent_dir = os.path.dirname(ffile).split("/")[-1]
        # # subfolders in the MAIL dir
        # _dest_dir = os.path.join(main_dir, "MAIL", _parent_dir)
        # # 
        # if not os.path.exists(_dest_dir):
            # os.makedirs(_dest_dir)
        # # create a file telling the folders contain mbox files
        # if not os.path.exists(os.path.join(main_dir,"MAIL","mbox_folders")):
            # _f = open(os.path.join(main_dir,"MAIL","mbox_folders"), "w")
            # _f.write("application/mbox")
            # _f.close()
        # # in indexerdb now
        # for _mitem in _mbox.items():
            # message = _mitem[1]
            # #metadata1 = message['date']+"\n"+message['from']+"\n"+message['subject']
            # # _mbox_add = mailbox.mbox(_dest_dir+"/"+str(message['from'])+" - "+str(message['date']))
            # ux_time = str(time())
            # if message['date']:
                # m_date = str(message['date'])
            # else:
                # m_date = ux_time
            # if message['from']:
                # m_from = str(message['from'])
            # else:
                # m_from = "Unknown"
            # if message['subject']:
                # m_subj = str(message['subject'])
            # else:
                # m_subj = "None"
            # metadata1 = m_date+"\n"+m_from+"\n"+m_subj
            # # _mbox_add = mailbox.mbox(_dest_dir+"/"+m_date+" - "+str(ux_time))
            # _mbox_add = mailbox.mbox(_dest_dir+"/"+m_date+" - "+m_from)
            # _mbox_add.add(message.as_string())
        # #
        # _mbox.close()
    
    
    # get the number of row clicking on each row
    def get_ffolder(self, listbox, listboxrow):
        global aii
        aii = listboxrow.get_index()
    
    # delete the selected entry from list by pressing button_delete
    def del_ffolder(self, widget):
        selection = self.listbox.get_selected_row()
        self.listbox.remove(selection)
        root.remove(root[aii])
        tree = ET.ElementTree(root)
        tree.write(CONFIG_XML)
    
####### tab 2
    # we need the argument 'active'
    def activate_cb(self, button, active, _comm, plugname):
        bstate = button.get_active()
        os.chdir(main_dir+"/extractors")
        if _comm:
            if bstate == True:
                try:
                    os.rename("disabled/"+plugname, plugname)
                except:
                    pass
            if bstate == False:
                try:
                    os.rename(plugname, "disabled/"+plugname)
                except:
                    pass
        else:
            button.set_active(False)
        os.chdir(main_dir)
        
####### tab 3
    def on_language_changed(self, widget):
        index = self.combo_search3a.get_active()
        model = self.combo_search3a.get_model()
        item = model[index]
        os.remove("languages/lang.py")
        os.chdir("languages/")
        os.symlink(item[0]+".py","lang.py")
        os.chdir(main_dir)
        
    def on_check_button_toggled(self, checkbutton100):
        global not_system_fm
        if checkbutton100.get_active():
            not_system_fm = False
            self.label100.set_sensitive(not_system_fm)
            self.entry100.set_sensitive(not_system_fm)
            self.button100.set_sensitive(not_system_fm)
            self.entry100.set_text('')
            try:
                with open("./DATA/FileManager","w") as f:
                    f.write('SYSTEM')
            except:
                pass
        else:
            not_system_fm = True
            self.label100.set_sensitive(not_system_fm)
            self.entry100.set_sensitive(not_system_fm)
            self.button100.set_sensitive(not_system_fm)
            
    
    def on_filemanager_changed(self, widget):
        fm_choise = self.entry100.get_text()
        if fm_choise != "":
            try:
                with open("./DATA/FileManager","w") as f:
                    f.write(fm_choise)
            except:
                pass

    def on_dellog(self, widget):
        os.unlink(main_dir+"/LOG/log")
        os.unlink(main_dir+"/LOG/file_discharged.log")
        os.unlink(main_dir+"/LOG/file_added.log")

M = MainWindow()
M.show_all()
Gtk.main()
