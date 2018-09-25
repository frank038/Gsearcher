#!/usr/bin/env python3
# by frank38
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
import sqlite3

# database icons
DBICON = "database.png"
DBICON1 = "database1.png"

# name of config file
CONFIG_XML = "./DATABASE/config.xml"
# directory del programma
main_dir = os.getcwd()
# directory HOME
homepath = str(Path.home())

sys.path.append(main_dir+'/'+'languages/')

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

import lang as l

DATABASE = "./DATABASE/default.db"
REAL_NAME_DB = os.path.realpath(DATABASE)

# list of databases
os.chdir("DATABASE")
ddatabases = glob.glob("*.db")
if "default.db" in ddatabases:
    ddatabases.remove("default.db")
os.chdir(main_dir)

# name of chosen database
db_chname = "" 

class MainWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Gsearcher Chooser")
        self.set_icon_from_file("DATA/icons/gsearcher.svg")
        self.connect("delete-event", Gtk.main_quit)
        self.set_border_width(5)
        self.set_default_size(1024, 800)
        self.set_resizable(True)
        # add grid
        self.grid = Gtk.Grid()
        self.add(self.grid)
        # vbox1 in self
        self.vbox1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.grid.attach(self.vbox1, 0,0,1,1)
        # scrolled window in vbox1
        self.scrolledwindow = Gtk.ScrolledWindow()
        self.scrolledwindow.set_hexpand(True)
        self.scrolledwindow.set_vexpand(True)
        self.scrolledwindow.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scrolledwindow.set_placement(Gtk.CornerType.TOP_LEFT)
        self.vbox1.pack_start(self.scrolledwindow, True, True, 0)
        # box for buttons
        self.hbox1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        self.hbox1.set_vexpand(False)
        self.grid.attach(self.hbox1, 0,1,1,1)
        # and buttons
        self.button_launch = Gtk.Button(l.Launch)
        self.hbox1.pack_start(self.button_launch, True, True, 0)
        self.button_launch.connect("clicked", self.on_launch)
        separator = Gtk.Separator()
        separator.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.hbox1.pack_start(separator, False, False, 1)
        self.button_select = Gtk.Button(l.Select)
        self.hbox1.pack_start(self.button_select, True, True, 0)
        self.button_add = Gtk.Button(l.Add)
        self.button_add.connect("clicked", self.on_add)
        self.hbox1.pack_start(self.button_add, True, True, 0)
        self.button_delete = Gtk.Button(l.Delete)
        #self.button_delete.connect("clicked", self.on_delete)
        self.hbox1.pack_start(self.button_delete, True, True, 0)
        separator = Gtk.Separator()
        separator.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.hbox1.pack_start(separator, False, False, 1)
        self.button_quit = Gtk.Button(l.Quit)
        self.button_quit.connect("clicked", Gtk.main_quit)
        self.hbox1.pack_start(self.button_quit, True, True, 0)
        # iconview
        self.liststore = Gtk.ListStore(Pixbuf, str)
        # 
        self.iconview = Gtk.IconView.new()
        self.iconview.set_model(self.liststore)
        self.iconview.set_activate_on_single_click(True)
        self.iconview.set_pixbuf_column(0)
        self.iconview.set_text_column(1)
        self.iconview.connect("item-activated", self.on_liststore_changed)
        self.scrolledwindow.add(self.iconview)
        self.button_delete.connect("clicked", self.on_delete)
        image = Gtk.Image()
        
        for item in ddatabases:
            if item in REAL_NAME_DB:
                image.set_from_file("DATA/icons/"+DBICON1)
                pixbuf = image.get_pixbuf()
                self.liststore.append([pixbuf, item])
            else:
                image.set_from_file("DATA/icons/"+DBICON)
                pixbuf = image.get_pixbuf()
                self.liststore.append([pixbuf, item])
        # function of button_select
        self.button_select.connect("clicked", self.on_select)
    
    def on_launch(self, widget):
        os.execl("./Gsearcher.py","&")
        Gtk.main_quit
    
    def on_liststore_changed(self, iconview, widget):
        global db_chname
        
        if iconview.get_selected_items() != None:
            rrow = iconview.get_selected_items()[0]

        model = iconview.get_model()
        text1 = model[rrow][1]

        db_chname = text1
    
    # remove a database
    def on_delete(self, widget):
        # messagebox
        mmessage = l.ChooseMessage1
        messagedialog1 = Gtk.MessageDialog(parent=self,
                                              flags=Gtk.DialogFlags.MODAL,
                                              type=Gtk.MessageType.WARNING,
                                              buttons=Gtk.ButtonsType.OK_CANCEL,
                                              message_format=mmessage)
        messagedialog1.connect("response", self.dialog_response1)
        messagedialog1.show()
    
    # detete the database - delete the database from liststore
    def on_delete2(self):

        iter = self.liststore.get_iter(self.iconview.get_selected_items()[0])
        self.liststore.remove(iter)
        
        try:
            os.chdir("DATABASE") 
            os.unlink(db_chname)
            os.unlink(db_chname[:-3]+".xml")
            if os.readlink("default.db") == db_chname:
                os.unlink("default.db")
                os.unlink("config.xml")
            os.chdir(main_dir)
        except:
            pass
    
    # messagebox
    def msgbox(self, widget, ddata):
        messagedialog1 = Gtk.MessageDialog(parent=self,
                                              flags=Gtk.DialogFlags.MODAL,
                                              type=Gtk.MessageType.WARNING,
                                              buttons=Gtk.ButtonsType.OK_CANCEL,
                                              message_format=ddata)
        messagedialog1.connect("response", self.dialog_response1)
        messagedialog1.show()
    
    def dialog_response1(self, messagedialog1, response_id):
        if response_id == Gtk.ResponseType.OK:
            self.on_delete2()
            messagedialog1.destroy()
        elif response_id == Gtk.ResponseType.CANCEL:
            messagedialog1.destroy()
        elif response_id == Gtk.ResponseType.DELETE_EVENT:
            messagedialog1.destroy()

    # add a new database
    def on_add(self, widget):
        ttitle=""
        Gtk.Dialog(parent=self, title=ttitle, flags=Gtk.DialogFlags.MODAL,
                            buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                            Gtk.STOCK_OK, Gtk.ResponseType.OK))
        appd = Gtk.Dialog()
        appd.set_default_response(Gtk.ResponseType.OK)
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box = appd.get_content_area()
        label = Gtk.Label(l.ChooseMessage2)
        vbox.pack_start(label, False, True, 0)
        entry = Gtk.Entry()
        vbox.pack_start(entry, False, True, 0)
        appd.add_button("OK",Gtk.ResponseType.OK)
        appd.add_button("CANCEL",Gtk.ResponseType.CANCEL)
        appd.set_default_size(550, 140)
        box.add(vbox)
        appd.show_all()
        response = appd.run()
        
        if response == Gtk.ResponseType.OK:
            eentry = str(entry.get_text())[0:30].replace('"','_')

            if (eentry.strip() != "") and (eentry.strip() != "default.db") and (eentry.strip() != "default"):
                if eentry[-3:] != ".db":
                    eentry = eentry+".db"
                os.chdir("DATABASE")

                con = sqlite3.connect(str(eentry))
                cur = con.cursor()
                cur.execute("""create virtual table tabella using fts4(name, mime, mtime, dir, content, metadata, tag1)""")
                con.close()
                # creates an empty config.xml
                fp = open(eentry[:-3]+".xml", 'w')
                fp.write('<config version="1.0">'+'\n'+'</config>')
                fp.close()
                os.chdir(main_dir)
                image = Gtk.Image()
                image.set_from_file("DATA/icons/"+DBICON)
                pixbuf = image.get_pixbuf()
                self.liststore.append([pixbuf, str(eentry)])
                appd.destroy()
            else:
                appd.destroy()
        else:
           appd.destroy()
        
    # select another database
    def on_select(self, widget):
        # db_chname is the database to be default
        # name of the config.xml related to database
        xml_chname = db_chname[:-3]+".xml"
        # remove the link to database and set the new one
        os.chdir("DATABASE")
        try:
            os.unlink("default.db")
        except:
            pass
        try:
            os.symlink(db_chname, "default.db")
        except:
            pass
        # remove the link to config.xml and set the new one
        try:
            os.unlink("config.xml")
        except:
            pass
        os.symlink(xml_chname,"config.xml")

        if len(self.liststore) > 0:
            # search for available databases
            dddatabases = glob.glob("*.db")
            try:
                dddatabases.remove("default.db")
            except:
                pass
            # find the database linked
            REAL_NAME_DDB = os.path.realpath(db_chname)
            image = Gtk.Image()
            for ditem in dddatabases:
                for row in self.liststore:
                    if row[1] == db_chname:
                        image.set_from_file(main_dir+"/DATA/icons/"+DBICON1)
                        pixbuf = image.get_pixbuf()
                        self.liststore.set(row.iter, 0, pixbuf)
                    else:
                        image.set_from_file(main_dir+"/DATA/icons/"+DBICON)
                        pixbuf = image.get_pixbuf()
                        self.liststore.set(row.iter, 0, pixbuf)
        
            # simple message box to inform the change has been made
            mmessage = l.ChooseMessage3
            messagedialog2 = Gtk.MessageDialog(parent=self,
                                                  flags=Gtk.DialogFlags.MODAL,
                                                  type=Gtk.MessageType.WARNING,
                                                  buttons=Gtk.ButtonsType.OK,
                                                  message_format=mmessage)
            messagedialog2.connect("response", self.dialog_response2)
            messagedialog2.show()
        
        else:
            pass

        os.chdir(main_dir)

    def dialog_response2(self, messagedialog2, response_id):
        if response_id == Gtk.ResponseType.OK:
            messagedialog2.destroy()
        elif response_id == Gtk.ResponseType.DELETE_EVENT:
            messagedialog2.destroy()
            
M = MainWindow()
M.show_all()
Gtk.main()
