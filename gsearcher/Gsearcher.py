#!/usr/bin/env python3

Number_version = "1.0.4"

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, Gio, Pango
from gi.repository.GdkPixbuf import Pixbuf
import os,stat
import sys
import glob
import importlib
from pathlib import Path
import sqlite3
import subprocess
import re
import shutil
from time import gmtime, strftime

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from cfg import *

# use markup
USE_MARKUP = True
# # width of the main window
# WWIDTH = 1100
# # height of the manin window
# EEIGHT = 800
# # name of config file
# CONFIG_XML = "./DATABASE/config.xml"

####### starting check
# check executable permissions
for ffile in ["Gsearcher_config.py","Gsearcher_choose_db.py","indexerdb.py"]:
    if not os.access(ffile,os.X_OK):
        try:
            os.chmod(ffile, 0o755)
        except Exception as E:
            print("ERRORS:", str(E))
            sys.exit()

# check for system folders
for ffile in ["DATABASE", "LOG"]:
    if not os.path.exists("DATABASE"):
        try:
            os.makedirs(os.path.join(os.getcwd(),"DATABASE"))
        except Exception as E:
            print("ERRORS:", str(E))
            sys.exit()

# empty the log files
for _ff in ["LOG/file_added.log","LOG/file_discharged.log","LOG/log"]:
    if os.path.exists(_ff):
        os.unlink(_ff)

#######

# program directory
main_dir = os.getcwd()
# home directory
homepath = str(Path.home())
fdir = "extractors/"
sys.path.append(main_dir+'/'+'extractors/')
sys.path.append(main_dir+'/'+'languages/')
# date and time
ddatettime = strftime("%Y %b %d %H:%M:%S", gmtime())

# checks if the link to the config file exists and it is a link
def cr_config():
    if not os.path.islink(CONFIG_XML):
        print("Problem with the link config.xml.")
        os.execl("./Gsearcher_choose_db.py","&")
        Gtk.main_quit

cr_config()

# loads the config.xml file
try:
    tree = ET.parse(CONFIG_XML)
except:
    print("Error with the config file: reinstall the program.")
    sys.exit()
else:
    root = tree.getroot()

# checks if all folders and files are in main directory
ffdrg = ["DATABASE","DATA","LOG","extractors","languages","Gsearcher_config.py","indexerdb.py","Gsearcher_choose_db.py"]
for ffdr in ffdrg:
    if not Path(ffdr).exists():
        print("{} not in place: reinstall the program".format(ffdr))
        sys.exit()

# checks if the link to the database default.db exists
is_database = False
DATABASE = "default.db"

# check if there is one database
os.chdir("DATABASE")
ddatabases = glob.glob("*.db")
if "default.db" in ddatabases:
    ddatabases.remove("default.db")

# if database.db is not a link delete it
if not os.path.islink(DATABASE):
    try:
        os.unlink("default.db")
    except:
        pass

# checks if there is the database to query
# opens DATABASE
REAL_NAME_DB = os.path.realpath(DATABASE)
# if no database a new one is created
if ddatabases == []:
    con = sqlite3.connect("example1.db")
    is_database = True
    cur = con.cursor()
    cur.execute("""create virtual table tabella using fts4(name, mime, mtime, dir, content, metadata, tag1)""")
    # then the link if it is not present
    if not os.path.islink(DATABASE):
        os.symlink("example1.db","default.db")
    os.chdir(main_dir)
# if there is one database at least
else:
    # if the link is not present
    if not os.path.islink(DATABASE):
        os.symlink("example1.db","default.db")
    con = sqlite3.connect(DATABASE)
    is_database = True
    cur = con.cursor()
    os.chdir(main_dir)

# checks if the file lang.py is in languages dir
# or creates it from the first language file it finds
os.chdir("languages")
lang_support = glob.glob('*.py')
# checks if lang.py is a link or delete it
try:
    if not os.path.islink("lang.py"):
        os.unlink("lang.py")
except:
    pass
# exits if no language files
if lang_support == []:
    print("NO LANGUAGE FILES FOUND!!! Reinstall the program.")
    sys.exit()
# delete from the list the link lang.py
if "lang.py" in lang_support:
    lang_support.remove("lang.py")
else:
    # otherwise creates the link
    if (lang_support != []):
        os.symlink(lang_support[0], "lang.py")

# checks if lang.py is a valid link - create a new one
if (not Path("lang.py").exists()):
    try:
        os.unlink("lang.py")
    except:
        pass
    os.symlink(lang_support[0], "lang.py")

os.chdir(main_dir)
l = importlib.import_module('lang')

# check if extractors commands are in system
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

CAN_INDEX = True

if ePlugins1 == []:
    print("NO VALID EXTRACTORS FOUND!!! At least one is required for the program to work.")
    CAN_INDEX = False
    sys.exit()
try:
    os.chdir("disabled")
except:
    print("Folder disabled non found: exiting...")
    sys.exit()

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
        print("Error while importing the plugin {}".format(ioe))

# if extractor command is not found, the plugin is disabled
la1 = 0
for ccommand in extractor_command:
    if ccommand == "TRUE":
        _comm = "INTERNAL"
    else:
        _comm = shutil.which(ccommand)
    _idx = extractor_command.index(ccommand)
    if (_comm == None) and (extractor_filename[_idx] not in ePlugins2) :
        # move the plugin away
        os.chdir("extractors")
        os.rename(extractor_filename[_idx],"disabled/"+extractor_filename[_idx])
        os.chdir(main_dir)
        # write error in the log file
        flog = open(main_dir+"/LOG/log","a")
        flog.write("{} The command {} cannot be found. The plugin {} has been disabled. The {} files cannot be indexed.\n".format(ddatettime,ccommand, extractor_filename[_idx], extractor_identify[_idx]))
        flog.close()
    la1 += 1

# combo_search initialization: And
combo_box_name = l.And

# # limits the number of opened tabs
# LIMIT_TAB = 10
# # for discharging useless tabs
# LIMIT_OFFSET = 250
# reads what file manager to use
file_manager = 'SYSTEM'
try:
    with open("./DATA/FileManager","r") as f:
        FM = f.readline()
        if FM != 'SYSTEM':
            file_manager = "{}".format(FM)
except:
    pass

class MainWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Gsearcher")
        self.set_icon_from_file("DATA/icons/gsearcher.svg")
        self.connect("delete-event", Gtk.main_quit)
        self.set_events(Gdk.EventMask.KEY_PRESS_MASK)
        self.connect('key-press-event', self.on_key_pressed)
        #
        _db_path = "DATABASE/default.db"
        if os.path.exists(_db_path) and os.path.islink(_db_path):
            _db_link = os.readlink(_db_path)
            if os.path.exists(os.path.join("DATABASE",_db_link)):
                _db_name = os.path.splitext(_db_link)[0]
                self.set_title("Gsearcher - "+_db_name)
        #
        self.set_border_width(5)
        self.set_default_size(WWIDTH, EEIGHT)
        self.set_resizable(True)
        # vertical box for all widgets
        self.hbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        self.hbox.set_homogeneous(False)
        self.add(self.hbox)
        # grid in hbox
        self.grid = Gtk.Grid()
        self.grid.set_column_homogeneous(True)
        #self.grid.set_row_homogeneous(True)
        self.hbox.pack_start(self.grid, True, True, 1)
        # menu in grid row 0
        self.menubar = Gtk.MenuBar()
        ### add menuitems
        # item1
        menuitem = Gtk.MenuItem(label=l.item1, right_justified=False)
        self.menubar.append(menuitem)
        # add submenu in item1
        menu = Gtk.Menu()
        menuitem.set_submenu(menu)
        # add submenu
        menuitem = Gtk.MenuItem(label=l.Open_database)
        menuitem.connect("activate", self.open_database)
        menu.append(menuitem)
        # add another submenu in item1
        menuitem = Gtk.MenuItem(label=l.Quit)
        menuitem.connect("activate", Gtk.main_quit)
        menu.append(menuitem)
        # item2
        menuitem = Gtk.MenuItem(label=l.item2, right_justified=False)
        self.menubar.append(menuitem)
        # add submenu in item2
        menu = Gtk.Menu()
        menuitem.set_submenu(menu)
        menuitem = Gtk.MenuItem(label=l.Index)
        menuitem.connect("activate", self.start_index)
        menu.append(menuitem)
        # add another submenu in item2
        menuitem = Gtk.MenuItem(label=l.Preference)
        menuitem.connect("activate", self.open_preference)
        menu.append(menuitem)
        # add another submenu in item2
        menuitem = Gtk.MenuItem(label=l.Erase)
        menuitem.connect("activate", self.er_database)
        menu.append(menuitem)
        # item3
        menuitem = Gtk.MenuItem(label=l.item3, right_justified=False)
        self.menubar.append(menuitem)
        ### added three menuitem
        # add submenu in item3
        menu = Gtk.Menu()
        menuitem.set_submenu(menu)
        menuitem = Gtk.MenuItem(label=l.Version+Number_version)
        menu.append(menuitem)
        # add another submenu in item3
        menuitem = Gtk.MenuItem(label=l.Usage)
        menuitem.connect("activate", self.on_guide)
        menu.append(menuitem)
        # attach the menubar to grid
        self.grid.attach(self.menubar, 0, 0, 1, 1)
        # horizontal box
        self.hbox_search = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        # combo box and-or
        self.liststore = Gtk.ListStore(str)
        self.liststore.append([l.And])
        self.liststore.append([l.Or])
        self.liststore.append([l.Metadata])
        self.combo_search = Gtk.ComboBox()
        self.combo_search.set_model(self.liststore)
        self.combo_search.set_active(0)
        self.combo_search.connect("changed", self.on_combo_search_changed)
        self.cellrenderertext = Gtk.CellRendererText()
        self.combo_search.pack_start(self.cellrenderertext, True)
        self.combo_search.add_attribute(self.cellrenderertext, "text", 0)
        self.hbox_search.pack_start(self.combo_search, False, False, 1)
        # entry for searching in hbox_search
        self.entry_search = Gtk.Entry()
        self.stext1 = ""
        self.hbox_search.pack_start(self.entry_search, True, True, 1)
        # button for search - connected to entry_search
        self.button_search = Gtk.Button(label=l.Search)
        self.hbox_search.pack_start(self.button_search, False, False, 1)
        # add separator
        separator = Gtk.Separator()
        separator.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.hbox_search.pack_start(separator, False, False, 1)
        # button for delete from database file
        #self.button_delete = Gtk.Button()
        #self.button_delete.set_label(label=l.Delete)
        #self.hbox_search.pack_start(self.button_delete, False, False, 1)
        # add separator
        separator = Gtk.Separator()
        separator.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.hbox_search.pack_start(separator, False, False, 1)
        # button - opens the directory of choosen file
        self.button_open_entry = Gtk.Button(label=l.Open)
        self.hbox_search.pack_start(self.button_open_entry, False, False, 1)
        # and then attach hbox_search to grid
        self.grid.attach(self.hbox_search, 0, 1, 1, 1)
        # scrollable treelist in grid row 2
         # id name type folder
        self.liststore1 = Gtk.ListStore(str, str, str, str)
        self.treeview1 = Gtk.TreeView()
        self.treeview1.set_model(self.liststore1)
        self.scrollable_treelist1 = Gtk.ScrolledWindow()
        self.scrollable_treelist1.set_vexpand(True)
        self.grid.attach(self.scrollable_treelist1, 0, 2, 1, 1)
        self.scrollable_treelist1.add(self.treeview1)
        cellrenderertext = Gtk.CellRendererText()
        # id
        treeviewcolumn = Gtk.TreeViewColumn("#")
        treeviewcolumn.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        self.treeview1.append_column(treeviewcolumn)
        treeviewcolumn.pack_start(cellrenderertext, True)
        treeviewcolumn.add_attribute(cellrenderertext, "text", 0)
        # name file
        treeviewcolumn = Gtk.TreeViewColumn(l.Name)
        treeviewcolumn.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        self.treeview1.append_column(treeviewcolumn)
        treeviewcolumn.pack_start(cellrenderertext, True)
        treeviewcolumn.add_attribute(cellrenderertext, "text", 1)
        # type
        treeviewcolumn = Gtk.TreeViewColumn(l.Type)
        treeviewcolumn.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        self.treeview1.append_column(treeviewcolumn)
        treeviewcolumn.pack_start(cellrenderertext, True)
        treeviewcolumn.add_attribute(cellrenderertext, "text", 2)
        # folder path
        treeviewcolumn = Gtk.TreeViewColumn(l.Folder)
        treeviewcolumn.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        self.treeview1.append_column(treeviewcolumn)
        treeviewcolumn.pack_start(cellrenderertext, True)
        treeviewcolumn.add_attribute(cellrenderertext, "text", 3)
        #
        self.selection1 = self.treeview1.get_selection()
        self.treeview1.set_activate_on_single_click(True)
        self.treeview1.connect("row-activated", self.on_liststore_changed)
        # notebook in grid at row 3 
        self.notebook = Gtk.Notebook()
        self.notebook.set_scrollable(True)
        self.grid.attach(self.notebook, 0, 3, 1, 1)
        self.page1 = Gtk.Box()
        self.page1.set_border_width(10)
        self.label1 = Gtk.Label()
        self.label1.set_text("   \n   \n   \n   ")
        self.page1.add(self.label1)
        self.notebook.append_page(self.page1, Gtk.Label(label=l.Abstract))
        # button_search function
        if is_database:
            self.button_search.connect("clicked", self.on_button_search)
        # button_open_entry
        self.button_open_entry.connect("clicked", self.on_open_fm)
        #self.button_delete.connect("clicked", self.on_delete_item)
        self.entry_search.grab_focus()
    
    # press return to query
    def on_key_pressed(self, widget, event):
        keyname = Gdk.keyval_name(event.keyval)
        if keyname == "Return":
            self.on_button_search(widget)
    
    # dialog to ask confirmation to empty the current database
    def er_database(self, widget):
        messagedialoge = Gtk.MessageDialog(parent=self,
                                          modal=True,
                                          message_type=Gtk.MessageType.WARNING,
                                          buttons=Gtk.ButtonsType.OK_CANCEL,
                                          text=l.IndexerMessage9)
        messagedialoge.connect("response", self.dialog_responsee)
        messagedialoge.show()
    
    def dialog_responsee(self, messagedialoge, response_id):
        if response_id == Gtk.ResponseType.OK:
            cur.execute("""delete from tabella""")
            con.commit()
            messagedialoge.destroy()
        elif response_id == Gtk.ResponseType.CANCEL:
            messagedialoge.destroy()
        elif response_id == Gtk.ResponseType.DELETE_EVENT:
            messagedialoge.destroy()
    
    # dialog to ask confirmation to delete from database the selected file
    def on_delete_item(self, widget):
        messagedialogd = Gtk.MessageDialog(parent=self,
                                          modal=True,
                                          message_type=Gtk.MessageType.WARNING,
                                          buttons=Gtk.ButtonsType.OK_CANCEL,
                                          text=l.IndexerMessage8)
        messagedialogd.connect("response", self.dialog_responsed)
        messagedialogd.show()
    
    def dialog_responsed(self, messagedialogd, response_id):
        if response_id == Gtk.ResponseType.OK:
            self.on_delete_item2(self.button_delete)
            messagedialogd.destroy()
        elif response_id == Gtk.ResponseType.CANCEL:
            messagedialogd.destroy()
        elif response_id == Gtk.ResponseType.DELETE_EVENT:
            messagedialogd.destroy()
    
    # function for the above dialog
    def on_delete_item2(self, widget):
        (model, iter) = self.selection1.get_selected()
        if iter != None:
            dname = model[iter][1]
            dfold = model[iter][3]
            try:
                cur.execute("""delete from tabella where name=(?) and dir=(?)""", (dname, dfold))
                con.commit()
            except:
                pass
    
    # chooses the database to open
    def open_database(self, widget):
        os.execl("./Gsearcher_choose_db.py","&")
        Gtk.main_quit
    
    # chooses the file manager to use
    def on_open_fm(self, widget):
        (model, iter) = self.selection1.get_selected()
        if iter != None:
            if file_manager == 'SYSTEM':
                try:
                    os.system("xdg-open '{}'".format(model[iter][3].replace("'","'\\''")))
                except:
                    print("System file manager: error.")
            else:
                try:
                    fffolder = str(model[iter][3]).replace("'","\'")
                    ccommand = str(file_manager.replace("%F",'"'+fffolder+'"'))
                    os.system("{}".format(ccommand))
                except:
                    print("Custom file manager: error.")
    
    # returns the combo_search choise - default And
    def on_combo_search_changed(self, combo_search):
        global combo_box_name
        tree_iter = self.combo_search.get_active_iter()
        if tree_iter != None:
            model = self.combo_search.get_model()
            combo_box_name = model[tree_iter][0]
        else:
            pass
    
    # return the file name of the selsected row
    # fill the notebook
    def on_liststore_changed(self, widget, row, col):
        model = widget.get_model()
        text0 = model[row][0]
        text1 = model[row][1]
        text2 = model[row][2]
        text3 = model[row][3]
        
        nfile_index = int(text0)
        namefile = text1
        pathfile = text3
        
        SEARCHING_FILE = (text1, text3)
        
        stext = self.stext1
        stext1 = []
        stext2 = ""
        
        if (combo_box_name == l.Or) or (combo_box_name == l.Metadata):
            stext1 = stext.split()
            for ww in range(len(stext1)-1):
                stext2 += """{} OR """.format(stext1[ww])
            stext2 += stext1[-1]
            stext = stext2
        # if Metadata is not the choise
        if not combo_box_name == l.Metadata:
            rrcontent = []
            cur.execute("""select offsets(tabella) from tabella where content match ?""", (stext,))
            rrcontent = cur.fetchall()

            listc = []
            for aet in range(len(rrcontent)):
                listc.append(rrcontent[aet][0].split())

            listb = [] 
            listb1 = []
            listf = []
             
            for kka in listc:
                if len(kka) > 4:
                    listd = []
                    for kkk in range(0,len(kka),4):
                        listd.append(int(kka[kkk]))
                        listd.append(int(kka[kkk+1]))
                        listd.append(int(kka[kkk+2]))
                        listd.append(int(kka[kkk+3]))
                        listf.append(listd[:])
                        listd = []
                    listb1.append(listf[:])
                    listf = []
                else:
                    listf.append(kka[:])
                    listb1.append(listf[:])
                    listf = []
            
            liste = listb1
            dg = 0
            iidxfe1 = 0
            iidxfe2 = 1
            listg = []
            for kka in liste[:]:

                if len(kka) > 1:
                    listaa = []
                    fe1 = kka[iidxfe1][2]
                    listaa.append(kka[iidxfe1])
                    for iidx in range(len(kka)-1):
                        if kka[iidxfe2][2] - kka[iidxfe1][2] > LIMIT_OFFSET:
                            listaa.append(kka[iidxfe2])
                            iidxfe1 = iidxfe2
                            iidxfe2 += 1
                        else:
                            iidxfe2 += 1
                    iidxfe1 = 0
                    iidxfe2 = 1
                    listb.append(listaa)

                else:
                    listb.append(kka)

            if len(listb) > 0:
                
                npg = self.notebook.get_n_pages()
                for ttab in range(npg):
                    self.notebook.remove_page(0)
                
                kk = listb[nfile_index-1]
                
                for kkk in kk:
                    if len(kk) > LIMIT_TAB:
                        dg = len(kk) - LIMIT_TAB
                        del kk[-dg:]
                    
                    if int(listb[listb.index(kk)][kk.index(kkk)][2]) < 197:
                        third_element = 0
                    else:
                        third_element = int(listb[listb.index(kk)][kk.index(kkk)][2])
                    if third_element < 393:
                        cur.execute("""select substr(content,?,392) from tabella where name=(?) and dir=(?)""", (third_element, namefile, pathfile))
                    elif third_element < 588:
                        cur.execute("""select substr(content,0,588) from tabella where name=(?) and dir=(?)""", (namefile, pathfile))
                    else:
                        cur.execute("""select substr(content,?,588) from tabella where name=(?) and dir=(?)""", (third_element-196, namefile, pathfile))
                    lnotebook_tuple = cur.fetchone()
                    lnotebook_list = lnotebook_tuple[0]
                    ## add tab(s)
                    page = Gtk.Box()
                    page.set_border_width(10)
                    label = Gtk.Label()
                    # split each line after 85 chars
                    aaaaa = ""
                    aaaaa += ('\n'.join(line.strip() for line in re.findall(r'.{1,85}(?:\s+|$)', lnotebook_list)))
                    # routine to set bold the searching word
                    temp = aaaaa.splitlines()
                    temp2 = []
                    
                    # list of searching terms
                    temp3 = stext.split()
                    # remove OR if or is chosed
                    try:
                        temp3.remove("OR")
                    except:
                        pass
                    
                    # use the markup or not
                    if USE_MARKUP:
                        dic = {x: '<b>'+x+'</b>' for x in temp3}
                        # replace and set to bold each searched word
                        def replace_all(text, dic):
                            for i, j in dic.items():
                                text = text.replace(i, j)
                            return text
    
                        aaaaal = replace_all(aaaaa.lower().replace("<", "&lt;").replace(">", "&gt;"),dic)
                        label.set_text(aaaaal)
                        label.set_use_markup(True)
                    elif not USE_MARKUP:
                        label.set_text(aaaaa)
                    #
                    page.add(label)
                    self.notebook.append_page(page, Gtk.Label(label=l.Abstract))
                    page.show()
                    label.show()
                
                # adds tab for METADATA
                cur.execute("""select metadata, tag1 from tabella where name=(?) and dir=(?)""", (namefile, pathfile))
                lmeta_tuple = cur.fetchone()
                lmeta_string = lmeta_tuple[0]
                lmeta_tag1 = lmeta_tuple[1]
                if lmeta_string != "":
                     # scrolled window
                    scrolledwindow = Gtk.ScrolledWindow()
                    scrolledwindow.set_hexpand(True)
                    scrolledwindow.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.NEVER)
                    scrolledwindow.set_placement(Gtk.CornerType.TOP_RIGHT)
                    labelm = Gtk.Label(xalign=0.3)
                    scrolledwindow.add(labelm)
                    labelm.set_text("\n"+lmeta_string)
                    labelm.modify_font(Pango.FontDescription('Mono'))
                    #
                    page = Gtk.Box()
                    page.set_border_width(10)
                    page.add(scrolledwindow)
                    self.notebook.prepend_page(page, Gtk.Label(label=l.Metadata))
                    labelm.show()
                    scrolledwindow.show()
                    page.show()
                # if tabs are more than LIMIT_TAB
                # adds a message tab
                if dg > 0:
                    labeldg = Gtk.Label(xalign=0.3)
                    labeldg.set_text(l.TNotice)
                    page = Gtk.Box()
                    page.set_border_width(10)
                    page.add(labeldg)
                    self.notebook.append_page(page, Gtk.Label(label=l.Notice))
                    page.show()
                    labeldg.show()
                # adds tab for TAG1
                if lmeta_tag1 != "":
                    labelt = Gtk.Label(xalign=0.3)
                    labelt.set_text("\n"+lmeta_tag1)
                    page = Gtk.Box()
                    page.set_border_width(10)
                    page.add(labelt)
                    self.notebook.append_page(page, Gtk.Label(label=l.Tag1))
                    labelt.show()
                    page.show()
        
        elif combo_box_name == "Metadata":
            cur.execute("""select metadata,content,tag1 from tabella where name=(?) and dir=(?)""", (namefile, pathfile))
            lmeta_tuple = cur.fetchone() 
            lmeta_string = lmeta_tuple[0]
            lcontent_string = lmeta_tuple[1][:396]
            lmeta_tag1 = lmeta_tuple[2]
            # removes all previous tabs
            npg = self.notebook.get_n_pages()
            for ttab in range(npg):
                self.notebook.remove_page(0)
            # scrolled window
            scrolledwindow = Gtk.ScrolledWindow()
            scrolledwindow.set_hexpand(True)
            scrolledwindow.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.NEVER)
            scrolledwindow.set_placement(Gtk.CornerType.TOP_RIGHT)
            # adds the METADATA tab
            labelm = Gtk.Label(xalign=0.3)
            scrolledwindow.add(labelm)
            labelm.set_text(lmeta_string)
            labelm.modify_font(Pango.FontDescription('Mono'))
            page = Gtk.Box()
            page.set_border_width(10)
            page.add(scrolledwindow)
            self.notebook.prepend_page(page, Gtk.Label(label=l.Metadata))
            labelm.show()
            scrolledwindow.show()
            page.show()
            # adds tab for TAG1
            if lmeta_tag1 != "":
                labelt = Gtk.Label(xalign=0.3)
                labelt.set_text("\n"+lmeta_tag1)
                page = Gtk.Box()
                page.set_border_width(10)
                page.add(labelt)
                self.notebook.append_page(page, Gtk.Label(label=l.Tag1))
                labelt.show()
                page.show()
            # adds one tab for content
            # each line up to 85 chars
            aaaaa = ""
            aaaaa += ('\n'.join(line.strip() for line in re.findall(r'.{1,85}(?:\s+|$)', lcontent_string)))
            aaaaal = aaaaa.lower()
            page = Gtk.Box()
            page.set_border_width(10)
            label = Gtk.Label()
            label.set_text("\n"+aaaaal)
            page.add(label)
            self.notebook.append_page(page, Gtk.Label(label=l.Abstract))
            label.show()
            page.show()
            

    # searches the finding words  
    # populate the liststore  
    def on_button_search(self, button):
        npg = self.notebook.get_n_pages()
        for ttab in range(npg):
            self.notebook.remove_page(0)
        page = Gtk.Box()
        page.set_border_width(10)
        label = Gtk.Label(label="  \n  \n  \n  ")
        page.add(label)
        self.notebook.append_page(page, Gtk.Label(label=l.Abstract))
        page.show()
        label.show()
        self.stext1 = self.entry_search.get_text().lower()
        stext = self.stext1

        if stext != "":
            # remove old entries
            if combo_box_name == l.And:
                if len(self.liststore1) != 0:
                    for i in range(len(self.liststore1)):
                        iter = self.liststore1.get_iter(0)
                        self.liststore1.remove(iter)

                cur.execute("""select name, mime, dir from tabella where content match ?""", (stext,))
                rae = cur.fetchall()
               
                for lenrae in range(len(rae)):
                    nname = rae[lenrae][0]
                    ttype = rae[lenrae][1]
                    ffolder = rae[lenrae][2]
                    self.liststore1.append([str(lenrae+1),nname,ttype, ffolder])

            if combo_box_name == l.Or:
                if len(self.liststore1) != 0:
                    for i in range(len(self.liststore1)):
                        iter = self.liststore1.get_iter(0)
                        self.liststore1.remove(iter)

                wlist = ""
                wlist1 = stext.strip().split()
                for ww in range(len(wlist1)-1):
                    wlist += """{} OR """.format(wlist1[ww])
                wlist += wlist1[-1]
                cur.execute("""select name, mime, dir from tabella where content match ?""", (wlist,))
                rae = cur.fetchall()
                for lenrae in range(len(rae)):
                    nname = rae[lenrae][0]
                    ttype = rae[lenrae][1]
                    ffolder = rae[lenrae][2]
                    self.liststore1.append([str(lenrae+1), nname,ttype, ffolder])

            if combo_box_name == l.Metadata:
                if len(self.liststore1) != 0:
                    for i in range(len(self.liststore1)):
                        iter = self.liststore1.get_iter(0)
                        self.liststore1.remove(iter)

                wlist = ""
                wlist1 = stext.strip().split()
                for ww in range(len(wlist1)-1):
                    wlist += """{} OR """.format(wlist1[ww])
                wlist += wlist1[-1]
                cur.execute("""select name, mime, dir from tabella where metadata match ? or tag1 match ?""", (wlist,wlist))
                rae = cur.fetchall()
                for lenrae in range(len(rae)):
                    nname = rae[lenrae][0]
                    ttype = rae[lenrae][1]
                    ffolder = rae[lenrae][2]
                    self.liststore1.append([str(lenrae+1), nname,ttype, ffolder])

    # routine to index the file in folders
    def start_index2(self):
        llist = []

        if CAN_INDEX == True:
            llist = subprocess.check_output('./indexerdb.py',universal_newlines=True,shell=True).split()
        else:
            llist = [-1]

        IMsg6 = ""
        IMsg10 = ""
        message0 = ""
        if int(llist[0] == -1):
            message0 = l.IndexerMessage11
        elif int(llist[4]) > 0:
            IMsg6 = "\n"+l.IndexerMessage6
        elif int(llist[5]) > 0:
            IMsg10 = "\n"+l.IndexerMessage10
        
        message1 = message0 or (l.IndexerMessage2+str(llist[0])+"\n"+l.IndexerMessage3+str(llist[1])+"\n"+l.IndexerMessage4+str(llist[2])+"\n"+l.IndexerMessage7+str(llist[3])+IMsg6+IMsg10)
        
        messagedialog1 = Gtk.MessageDialog(parent=self,
                                          modal=True,
                                          message_type=Gtk.MessageType.WARNING,
                                          buttons=Gtk.ButtonsType.OK,
                                          text=message1)
        messagedialog1.connect("response", self.dialog_response1)
        messagedialog1.show()
    
    def dialog_response1(self, messagedialog1, response_id):
        if response_id == Gtk.ResponseType.OK:
            messagedialog1.destroy()
        elif response_id == Gtk.ResponseType.DELETE_EVENT:
            messagedialog1.destroy()
    
    def start_index(self, widget):
        message3 = l.IndexerMessage5
        messagedialog3 = Gtk.MessageDialog(parent=self,
                                          modal=True,
                                          message_type=Gtk.MessageType.WARNING,
                                          buttons=Gtk.ButtonsType.OK_CANCEL,
                                          text=message3)
        messagedialog3.connect("response", self.dialog_response3)
        messagedialog3.show()
    
    def dialog_response3(self, messagedialog3, response_id):
        if response_id == Gtk.ResponseType.OK:
            self.start_index2()
            messagedialog3.destroy()
        else:
            messagedialog3.destroy()
    
    def open_preference(self, widget):
        os.execl("./Gsearcher_config.py","&")
        Gtk.main_quit

    def on_guide(self, widget):
        messagedialog2 = Gtk.MessageDialog(parent=self,
                                          modal=True,
                                          message_type=Gtk.MessageType.WARNING,
                                          buttons=Gtk.ButtonsType.OK,
                                          text=l.Help)
        messagedialog2.connect("response", self.dialog_response2)
        messagedialog2.show()
    
    def dialog_response2(self, messagedialog2, response_id):
        if response_id == Gtk.ResponseType.OK:
            messagedialog2.destroy()
        elif response_id == Gtk.ResponseType.DELETE_EVENT:
            messagedialog2.destroy()

def main():
    M = MainWindow()
    M.show_all()
    Gtk.main()
    return 0

if __name__ == '__main__':
    main()
