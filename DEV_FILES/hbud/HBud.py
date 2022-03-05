#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi, srt, azapi, json, os, sys, gettext, locale, acoustid, musicbrainzngs#, ctypes
from concurrent import futures
from time import sleep, time
from operator import itemgetter
from collections import deque
from datetime import timedelta
from random import sample
from mediafile import MediaFile, MediaField, MP3DescStorageStyle, StorageStyle
gi.require_version('Gtk', '3.0')
gi.require_version('Keybinder', '3.0')
from gi.repository import Gtk, GLib, GdkPixbuf, Gdk, Keybinder
from hbud import letrasapi, musixapi, helper, tools, vlc
from hbud.stopwatch import Stopwatch
stopwatch = Stopwatch()

class Main(helper.Widgets):
    def __init__(self):
        super(Main, self).__init__()
    
    def on_activate(self, app):
        APP = "io.github.swanux.hbud"
        WHERE_AM_I = os.path.abspath(os.path.dirname(__file__))
        LOCALE_DIR = os.path.join(WHERE_AM_I, 'locale/mo')
        print(LOCALE_DIR, locale.getlocale())
        locale.setlocale(locale.LC_ALL, locale.getlocale())
        locale.bindtextdomain(APP, LOCALE_DIR)
        gettext.bindtextdomain(APP, LOCALE_DIR)
        gettext.textdomain(APP)
        self._ = gettext.gettext
        self.API_KEY = "tnqJHZRTQL"
        musicbrainzngs.set_useragent("hbud", "0.3.5", "https://github.com/swanux/hbud")
        version = "HBud 0.3.5 Vereena"
        try:
            self.clickedE = sys.argv[1].replace("file://", "")
            if os.path.splitext(self.clickedE)[-1] not in self.supportedList and os.path.splitext(self.clickedE)[-1] != "":
                self.useMode = "video" 
                print("video, now", self.clickedE)
        except:
            self.clickedE = False
        self.builder.connect_signals(self)
        buffer = Gtk.TextBuffer()
        buffer.set_text(self._("""
 v0.3.5 - ??? ?? 2022 :

        * Complete rebase on libVLC v3 (instead of GStreamer)
        * Show current time when dragging slider
        * Numerous bugfixes
        * Performance optimizations (video playback 6-12x less CPU usage)
        * Complete migration to flatpak
"""))
        self.builder.get_object("whView").set_buffer(buffer)
        image_filter = Gtk.FileFilter()
        image_filter.set_name(self._("Image files"))
        image_filter.add_mime_type("image/*")
        self.iChoser.add_filter(image_filter)
        self.DAPI = azapi.AZlyrics('duckduckgo', accuracy=0.65)
        self.sSize, self.sMarg = int(float(sSize)), int(float(sMarg))
        self.size3, self.size4 = self.sSize*450, float(f"0.0{self.sMarg}")*450
        self.subSpin.set_value(self.sSize)
        self.subMarSpin.set_value(self.sMarg)
        self.size, self.size2 = 35000, 15000
        self.darke = dark == "True"
        self.musixe = musix == "True"
        self.azlyre = azlyr == "True"
        self.letrase = letras == "True"
        self.cover_size = coverSize
        self.slider.connect("button-release-event", self.on_slider_seek)
        self.slider.connect("value-changed", self.on_slider_grabbed)
        self.slider.connect("button-press-event", self.on_slider_grab)
        self.slider.connect("enter-notify-event", self.mouse_enter)
        self.slider.connect("leave-notify-event", self.mouse_leave)
        self.color, self.rounded = color, rounded
        coco = Gdk.RGBA()
        coco.parse(self.color)
        self.colorer.set_rgba(coco)
        self.roundSpin.set_value(float(self.rounded))
        self.dark_switch.set_state(self.darke)
        self.mus_switch.set_state(self.musixe)
        self.az_switch.set_state(self.azlyre)
        self.comboSize.set_active_id(str(self.cover_size))
        self.letr_switch.set_state(self.letrase)
        GLib.idle_add(self.subcheck.hide)
        GLib.idle_add(self.builder.get_object("oplink").set_label, self._("Visit OpenSubtitles"))
        GLib.idle_add(self.builder.get_object("sublink").set_label, self._("Visit Subscene"))
        self.sub.connect('size-allocate', self._on_size_allocated)
        self.window.connect('size-allocate', self._on_size_allocated0)
        tools.themer(self.provider, self.window, self.rounded, self.color)
        self.settings.set_property("gtk-application-prefer-dark-theme", self.darke)
        # Display the program
        self.window.set_title(version)
        self.window.set_application(app)
        self.window.show_all()
        self.createPipeline("local")
        self.topBox.hide()
        self.drop_but.hide()
        self.locBut.set_active(True)
        if self.clickedE:
            if self.useMode == "audio":
                self.loader("xy")
                self.on_playBut_clicked("xy")
            else:
                self.strBut.set_active(True)
                self.on_playBut_clicked("xy")
        self.on_key() # Init keybindings

    def highlight(self, widget, event):
        if event.button == 3:
            self.ednum = int(widget.get_name().replace("trackbox_", ""))
            menu = Gtk.Menu()
            menu.set_can_focus(False)
            menu_item = Gtk.MenuItem.new_with_label(self._('Delete from current playqueue'))
            menu_item.set_can_focus(False)
            menu_item.connect("activate", self.del_cur)
            menu.add(menu_item)
            menu_item = Gtk.MenuItem.new_with_label(self._('Edit metadata'))
            menu_item.set_can_focus(False)
            menu_item.connect("activate", self.ed_cur)
            menu.add(menu_item)
            menu.show_all()
            menu.popup_at_pointer()
        else:
            self.tnum = int(widget.get_name().replace("trackbox_", ""))
            tools.themer(self.provider, self.window, self.rounded, self.color, self.tnum)
            self.on_next("clickMode")

    def on_search(self, widget):
        term = widget.get_text().lower()
        GLib.idle_add(self.supBox.show_all)
        if term != "":
            results = []
            for i, item in enumerate(self.playlist):
                if term in item["title"].lower() or term in item["artist"].lower() or term in item["album"].lower():
                    results.append(i)
            for i, item in enumerate(self.supBox.get_children()):
                if i not in results: GLib.idle_add(item.hide)

    def on_sort_change(self, widget):
        aid = int(widget.get_active_id())
        if self.sorted == False: self.archive = self.playlist
        self.sorted = True
        if aid == 0 and self.sorted == True:
            self.playlist = self.archive
            self.sorted = False
        else: self.playlist = sorted(self.archive, key=itemgetter(self.searchDict[str(aid)][0]),reverse=self.searchDict[str(aid)][1])
        self.neo_playlist_gen()
        num = 0
        for item in self.playlist:
            if item["title"] == self.title: break
            else: num += 1
        self.tnum = num
        tools.themer(self.provider, self.window, self.rounded, self.color, self.tnum)

    def on_clear_order(self, _): os.system(f"rm {self.folderPath}/.saved.order")

    def on_rescan_order(self, _):
        GLib.idle_add(self.loader, self.folderPath, True)

    def on_order_save(self, _):
        f = open(f"{self.folderPath}/.saved.order", "w+")
        f.write(json.dumps(self.playlist))
        f.close()

    def _realized(self, widget, _=None):
        # x11 = ctypes.cdll.LoadLibrary('libX11.so')
        # x11.XInitThreads()
        self.videoPipe = self.vlcInstance.media_player_new()
        win_id = widget.get_window().get_xid()
        self.videoPipe.set_xwindow(win_id)
        self.videoPipe.event_manager().event_attach(vlc.EventType.MediaPlayerEndReached, self.media_end_reached)
        self.videoPipe.event_manager().event_attach(vlc.EventType.MediaPlayerTimeChanged, self.media_time_changed)

    def draw_event(self, _, cairo_ctx):
        cairo_ctx.set_source_rgb(0, 0, 0)
        cairo_ctx.paint()

    def createPipeline(self, mode):
        if mode == "local":
            self.vlcInstance = vlc.Instance("--no-xlib")
            self.audioPipe = self.vlcInstance.media_player_new()
            self.audioPipe.event_manager().event_attach(vlc.EventType.MediaPlayerEndReached, self.media_end_reached)
            self.audioPipe.event_manager().event_attach(vlc.EventType.MediaPlayerTimeChanged, self.media_time_changed)
            drawer = self.builder.get_object("drawer")
            self.strOverlay.add_overlay(self.theTitle)
            drawer.set_events(256)
            drawer.connect("button_press_event", self.mouse_click0)
            drawer.connect("realize",self._realized)
            drawer.connect("draw", self.draw_event)
            drawer.show()

    def on_dropped(self, button):
        if self.drop_but.get_visible() == True:
            if self.topBox.get_visible() == False:
                GLib.idle_add(self.drop_but.get_image().set_from_icon_name, "gtk-go-up", Gtk.IconSize.BUTTON)
                GLib.idle_add(self.topBox.show)
                self.search_play.grab_focus()
            elif button != "key":
                GLib.idle_add(self.drop_but.get_image().set_from_icon_name, "gtk-go-down", Gtk.IconSize.BUTTON)
                GLib.idle_add(self.topBox.hide)

    def allToggle(self, button):
        btn = Gtk.Buildable.get_name(button)
        if self.mainStack.get_visible_child() != self.switchDict[btn][0] and button.get_active() == True:
            self.mainStack.set_visible_child(self.switchDict[btn][0])
            if btn != "infBut" or self.nowIn == "video":
                GLib.idle_add(self.exBot.show)
                if btn == "locBut":
                    GLib.idle_add(self.trackCover.show)
                    GLib.idle_add(self.shuffBut.show)
                    if self.playlistPlayer == True: GLib.idle_add(self.drop_but.show)
                    GLib.idle_add(self.subcheck.hide)
                else:
                    GLib.idle_add(self.trackCover.hide)
                    GLib.idle_add(self.shuffBut.hide)
                    GLib.idle_add(self.drop_but.hide)
                    GLib.idle_add(self.subcheck.show)
                GLib.idle_add(self.karaokeIcon.set_from_icon_name, self.switchDict[btn][1], Gtk.IconSize.BUTTON)
                if self.playing == True:
                    if self.switchDict[btn][2] == "video" and self.nowIn == "audio": self.on_playBut_clicked("xy")
                    elif self.nowIn == "video" and self.switchDict[btn][2] != "video": self.on_playBut_clicked("xy")
                self.useMode = self.switchDict[btn][2]
            if btn == "infBut":
                GLib.idle_add(self.exBot.hide)
                GLib.idle_add(self.subcheck.hide)
                GLib.idle_add(self.drop_but.hide)
            GLib.idle_add(self.subcheck.set_state, False)
            GLib.idle_add(self.switchDict[btn][3].set_active, False)
            GLib.idle_add(self.switchDict[btn][4].set_active, False)
        elif self.mainStack.get_visible_child() == self.switchDict[btn][0]: GLib.idle_add(button.set_active, True) 

    def cleaner(self, widget):
        lis = widget.get_children()
        if lis == []: pass
        else: [i.destroy() for i in lis]
    
    def neo_playlist_gen(self, name="", src=0, dst=0):
        if name == 'shuffle':
            if self.playlistPlayer == True:
                playlistLoc = sample(self.playlist, len(self.playlist))
                self.playlist, self.tnum = playlistLoc, 0
                self.neo_playlist_gen()
                self.on_next('clickMode0')
        elif name == "rename":
            srcBox = self.supBox.get_children()[src]
            self.supBox.reorder_child(srcBox, dst)
            tmpList = self.supBox.get_children()
            for i in range(len(self.playlist)):
                tmpList[i].set_name(f"trackbox_{i}")
            if self.tnum == src or self.tnum == dst:
                if self.tnum == src: self.tnum = dst
                elif src > dst: self.tnum += 1
                elif src < dst: self.tnum -= 1
            else:
                if src > self.tnum and dst < self.tnum: self.tnum += 1
                elif src < self.tnum and dst > self.tnum: self.tnum -= 1
            tools.themer(self.provider, self.window, self.rounded, self.color, self.tnum)
        else:
            self.cleaner(self.playlistBox)
            self.supBox = Gtk.Box.new(1, 0)
            self.supBox.set_can_focus(False)
            for i, item in enumerate(self.playlist):
                trBox = helper.TrackBox(item["title"].replace("&", "&amp;"), item["artist"], i, item["year"], item["length"], item["album"])
                trBox.connect("button_release_event", self.highlight)
                trBox.connect('drag-drop', self._sig_drag_drop)
                trBox.connect('drag-end', self._sig_drag_end)
                self.supBox.pack_start(trBox, False, False, 0)
            yetScroll = Gtk.ScrolledWindow()
            yetScroll.set_can_focus(False)
            yetScroll.set_vexpand(True)
            yetScroll.set_hexpand(True)
            yetScroll.set_margin_end(10)
            yetScroll.add(self.supBox)
            self.playlistBox.pack_end(yetScroll, True, True, 0)
            yetScroll.show_all()
            self.adj = yetScroll.get_vadjustment()
            self.playlistPlayer = True
            if self.title != None:
                num = 0
                for item in self.playlist:
                    if item["title"] == self.title: break
                    else: num += 1
                self.tnum = num
                tools.themer(self.provider, self.window, self.rounded, self.color, self.tnum)
            GLib.idle_add(self.drop_but.show)

    def metas(self, location, extrapath, misc=False):
        f = MediaFile(f"{location}")
        title, artist, album, year, length = f.title, f.artist, f.album, f.year, str(timedelta(seconds=round(f.length))).replace("0:", "")
        if not title: title = os.path.splitext(extrapath)[0]
        if not artist: artist = self._("Unknown")
        if not album: album = self._("Unknown")
        if not year: year = 0
        itmp = {"uri" : location, "title" : title, "artist" : artist, "year" : year, "album" : album, "length" : length}
        if misc == True:
            if itmp not in self.playlist: self.pltmp.append(itmp)
        else: self.pltmp.append(itmp)

    def loader(self, path, misc=False):
        self.pltmp = []
        if self.clickedE:
            self.metas(self.clickedE, self.clickedE.split("/")[-1])
        else:
            pltmpin = os.listdir(path)
            for i in pltmpin:
                ityp = os.path.splitext(i)[1]
                if ityp in self.supportedList:
                    self.metas(f"{path}/{i}", i, misc)
        if misc == False: self.playlist = self.pltmp
        else: [self.playlist.append(item) for item in self.pltmp]
        GLib.idle_add(self.neo_playlist_gen)

    def on_openFolderBut_clicked(self, *_):
        if self.playing == True: self.pause()
        if self.useMode == "audio":
            self.fcconstructer(self._("Please choose a folder"), Gtk.FileChooserAction.SELECT_FOLDER, self._("Music"))
        else:
            self.fcconstructer(self._("Please choose a video file"), Gtk.FileChooserAction.OPEN, self._("Videos"))     

    def fcconstructer(self, title, action, folder):
        filechooserdialog = Gtk.FileChooserDialog(title=title, parent=self.window, action=action)
        if folder == self._("Videos"):
            filterr = Gtk.FileFilter()
            filterr.set_name(self._("Video files"))
            filterr.add_mime_type("video/*")
            filechooserdialog.add_filter(filterr)
        filechooserdialog.add_button(self._("_Cancel"), Gtk.ResponseType.CANCEL)
        filechooserdialog.add_button(self._("_Open"), Gtk.ResponseType.OK)
        filechooserdialog.set_default_response(Gtk.ResponseType.OK)
        filechooserdialog.set_current_folder(f"/home/{user}/{folder}")
        response = filechooserdialog.run()
        if response == Gtk.ResponseType.OK:
            if folder == self._("Music"):
                self.folderPath = filechooserdialog.get_uri().replace("file://", "")
                print("Folder selected: " + self.folderPath)
                if os.path.isfile(f"{self.folderPath}/.saved.order"):
                    f = open(f"{self.folderPath}/.saved.order", "r")
                    self.playlist = json.loads(f.read())
                    f.close()
                    for item in self.playlist[:]:
                        if os.path.isfile(f"{item['uri']}") == False: self.playlist.remove(item)
                    GLib.idle_add(self.neo_playlist_gen)
                else:
                    d_pl = futures.ThreadPoolExecutor(max_workers=4)
                    d_pl.submit(self.loader, self.folderPath)
            else:
                videoPath = filechooserdialog.get_filename()
                print("File selected: " + videoPath)
                self.on_playBut_clicked(videoPath)
        elif response == Gtk.ResponseType.CANCEL: print("Cancel clicked")
        filechooserdialog.destroy()

    def on_iChoser_file_set(self, *_):
        path = self.iChoser.get_filename()
        tf = open(path, "rb")
        tmBin = tf.read()
        tf.close()
        GLib.idle_add(self.load_cover, "brainz", tmBin)

    def on_save(self, *_):
        self.yrEnt.update()
        f = MediaFile(self.editingFile)
        f.year, f.artist, f.album, f.title, f.art = self.yrEnt.get_value_as_int(), self.arEnt.get_text(), self.alEnt.get_text(), self.tiEnt.get_text(), self.binary
        f.save()
        self.playlist[self.ednum]["year"] = self.yrEnt.get_value_as_int()
        self.playlist[self.ednum]["artist"] = self.arEnt.get_text()
        self.playlist[self.ednum]["album"] = self.alEnt.get_text()
        self.playlist[self.ednum]["title"] = self.tiEnt.get_text()
        if os.path.isfile(f"{self.folderPath}/.saved.order"):
            self.on_order_save()
        self.sub2_hide("xy")
        self.neo_playlist_gen()

    def sub2_hide(self, *_):
        self.sub2.hide()
        if self.magiStack.get_visible_child() == self.magiSpin:
            self.aborte = True
        GLib.idle_add(self.magiStack.set_visible_child, self.magiBut)
        return True

    def ed_cur(self, *_):
        self.editingFile = self.playlist[self.ednum]["uri"]
        self.yrEnt.set_value(self.playlist[self.ednum]["year"])
        self.arEnt.set_text(self.playlist[self.ednum]["artist"])
        self.alEnt.set_text(self.playlist[self.ednum]["album"])
        self.tiEnt.set_text(self.playlist[self.ednum]["title"])
        self.load_cover(mode="meta")
        self.sub2.set_title(self._("Edit metadata for")+str({self.editingFile.split('/')[-1]}))
        self.sub2.show_all()

    def on_magiBut_clicked(self, _):
        GLib.idle_add(self.magiStack.set_visible_child, self.magiSpin)
        thread = futures.ThreadPoolExecutor(max_workers=2)
        thread.submit(self.fetch_cur)

    def chose_one(self):
        liststore = Gtk.ListStore(str, str, str, int)
        for item in self.chosefrom:
            liststore.append([item["title"], item["artist"], item["album"], item["year"]])
        liststore.append([self._("None of the above"), "", "", 0])
        treeview = Gtk.TreeView(model=liststore)
        treeview.set_headers_visible(True)
        treeview.connect("row-activated", self.on_tree_row_activated)
        rendererText = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Title", rendererText, text=0)
        treeview.append_column(column)
        column = Gtk.TreeViewColumn("Artist", rendererText, text=1)
        treeview.append_column(column)
        column = Gtk.TreeViewColumn("Album", rendererText, text=2)
        treeview.append_column(column)
        column = Gtk.TreeViewColumn("Year", rendererText, text=3)
        treeview.append_column(column)
        self.choser_window.add(treeview)
        self.choser_window.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.choser_window.set_titlebar(self.headerbar)
        self.choser_window.set_title(self._("Which one is correct?"))
        GLib.idle_add(self.choser_window.show_all)
    
    def on_tree_row_activated(self, widget, row, _):
        row = row.get_indices()[0]
        if row != len(self.chosefrom):
            data = [self.chosefrom[row]["artist"], self.chosefrom[row]["title"], self.chosefrom[row]["rid"], self.chosefrom[row]["year"], self.chosefrom[row]["album"], self.chosefrom[row]["album_ids"]]
            thread = futures.ThreadPoolExecutor(max_workers=2)
            thread.submit(self.next_fetch, data)
        else: GLib.idle_add(self.magiStack.set_visible_child, self.magiBut)
        GLib.idle_add(self.choser_window.hide)
        GLib.idle_add(self.cleaner, self.choser_window)

    def fetch_cur(self):
        path = self.playlist[self.ednum]["uri"]
        try:
            results = acoustid.match(self.API_KEY, path, force_fpcalc=True)
        except acoustid.NoBackendError:
            print("chromaprint library/tool not found", file=sys.stderr)
        except acoustid.FingerprintGenerationError:
            print("fingerprint could not be calculated", file=sys.stderr)
        except acoustid.WebServiceError as exc:
            print("web service request failed:", exc.message, file=sys.stderr)
        self.chosefrom, i = [], 0
        try:
            for score, rid, title, artist in results:
                if self.aborte == True:
                    print("Aborted")
                    break
                if artist != None and title != None and i <= 10:
                    tmpData = musicbrainzngs.get_recording_by_id(rid, includes=["releases"])["recording"]["release-list"]
                    sleep(1.1)
                    i += 1
                    if len(tmpData) > 2:
                        tmpDir = {"score": score, "rid": rid, "title": title, "artist": artist, 'year' : int(tmpData[0]["date"].split("-")[0]), "album" : tmpData[0]["title"], "album_ids" : [d['id'] for d in tmpData if 'id' in d]}
                        for item in self.chosefrom:
                            if item["title"] == tmpDir["title"] and item["artist"] == tmpDir["artist"] and item["year"] == tmpDir["year"]: break
                        else: self.chosefrom.append(tmpDir)
        except: print("Something bad happened...")
        if self.aborte == True:
            print("Aborted")
            self.aborte = False
            return
        if len(self.chosefrom) == 0:
            GLib.idle_add(tools.diabuilder, self._('Did not find any match online.'), self._("Information"), Gtk.MessageType.INFO, Gtk.ButtonsType.OK, self.window)
            GLib.idle_add(self.magiStack.set_visible_child, self.magiBut)
        elif len(self.chosefrom) == 1:
            data = [self.chosefrom[0]["artist"], self.chosefrom[0]["title"], self.chosefrom[0]["rid"], self.chosefrom[0]["year"], self.chosefrom[0]["album"], self.chosefrom[0]["album_ids"]]
            thread = futures.ThreadPoolExecutor(max_workers=2)
            thread.submit(self.next_fetch, data)
        else: self.chose_one()
            
    def next_fetch(self, data):
        for i in range(10):
            if self.aborte == True:
                print("Aborted")
                self.aborte = False
                break
            print("Trying to get cover: "+str(i))
            try:
                release = musicbrainzngs.get_image_front(data[5][i], self.cover_size)
                sleep(1.2)
                print("Cover found")
                break
            except: release = None
        GLib.idle_add(self.yrEnt.set_value, data[3])
        GLib.idle_add(self.arEnt.set_text, data[0])
        GLib.idle_add(self.alEnt.set_text, data[4])
        GLib.idle_add(self.tiEnt.set_text, data[1])
        if release != None: GLib.idle_add(self.load_cover, "brainz", release)
        GLib.idle_add(self.magiStack.set_visible_child, self.magiBut)

    def mouse_click0(self, _, event):
        if event.type == Gdk.EventType._2BUTTON_PRESS: 
            if self.useMode == "video": self.on_karaoke_activate(0)
        elif event.type == Gdk.EventType.BUTTON_PRESS: self.on_playBut_clicked("")

    def del_cur(self, *_):
        self.playlist.remove(self.playlist[self.ednum])
        self.neo_playlist_gen()
        if self.tnum == self.ednum: self.play()

    def failsafe(self):
        try:
            if self.player.get_state() == vlc.State.Paused or self.player.get_state() == vlc.State.NothingSpecial or self.player.get_state() == vlc.State.Stopped: print("No playbin yet to pause")
            else: self.pause()
        except: print("No playbin yet to pause")

    def on_next(self, button):
        self.stopKar = True
        if self.nowIn == self.useMode or "clickMode" in button:
            if self.nowIn == "audio" or "clickMode" in button:
                if "clickMode" not in button:
                    self.tnum += 1
                    if self.tnum >= len(self.playlist): self.tnum = 0
                elif button == "clickMode0": self.tnum = 0
                self.failsafe()
                self.play()
                if self.sub.get_visible(): self.on_karaoke_activate("xy")
                if self.useMode == "audio" and button != "clickMode": self.adj.set_value(self.tnum*72-140)
            elif self.nowIn == "video":
                self.player.set_time(int(self.player.get_time() + 10*1000))

    def load_cover(self, mode="", bitMage=""):
        if mode == "meta": self.binary = MediaFile(self.editingFile).art
        elif mode == "brainz": self.binary = bitMage
        else: self.binary = MediaFile(self.url).art
        if not self.binary: tmpLoc = "hbud/icons/track.png"
        else:
            tmpLoc = "/tmp/cacheCover.jpg"
            f = open(tmpLoc, "wb")
            f.write(self.binary)
            f.close()
        coverBuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(tmpLoc, 80, 80, True)
        if mode == "meta" or mode == "brainz": GLib.idle_add(self.metaCover.set_from_pixbuf, coverBuf)
        else: GLib.idle_add(self.trackCover.set_from_pixbuf, coverBuf)

    def on_prev(self, *_):
        self.stopKar = True
        if self.nowIn == self.useMode:
            if self.nowIn == "audio":
                self.tnum -= 1
                if self.tnum < 0: self.tnum = len(self.playlist)-1
                self.failsafe()
                self.play()
                if self.sub.get_visible(): self.on_karaoke_activate("xy")
                if self.useMode == "audio": self.adj.set_value(self.tnum*72-140)
            elif self.nowIn == "video":
                self.player.set_time(int(self.player.get_time() - 10*1000))

    def stop(self, arg=False):
        if self.nowIn == "audio":
            stopwatch.stop()
            stopwatch.reset()
        print("Stop")
        GLib.idle_add(self.player.stop)
        if self.nowIn == "audio": self.audioPipe = self.player
        elif self.nowIn == "video": self.videoPipe = self.player
        self.playing = False
        self.label.set_text("0:00:00")
        GLib.idle_add(self.plaicon.set_from_icon_name, "media-playback-start", Gtk.IconSize.BUTTON)
        self.slider.set_value(0)
        self.res = arg

    def pause(self, *_): 
        print("Pause")
        if self.nowIn == "audio": stopwatch.stop()
        self.playing = False
        try:
            GLib.idle_add(self.plaicon.set_from_icon_name, "media-playback-start", Gtk.IconSize.BUTTON)
            self.player.pause()
        except: print("Pause exception")
    
    def resume(self):
        print("Resume")
        if self.nowIn == "audio": stopwatch.start()
        self.playing = True
        self.player.play()
        GLib.idle_add(self.plaicon.set_from_icon_name, "media-playback-pause", Gtk.IconSize.BUTTON)

    def on_slider_grab(self, *_):
        self.seeking = True
    
    def on_slider_grabbed(self, *_):
        current_time = str(timedelta(seconds=round(self.slider.get_value())))
        GLib.idle_add(self.slider.set_tooltip_text, f"{current_time}")

    def on_slider_seek(self, *_):
        if self.useMode == self.nowIn:
            seek_time_secs = self.slider.get_value()
            final_seek = int(seek_time_secs * 1000)
            if seek_time_secs < self.position:
                self.seekBack = True
            self.player.set_time(final_seek)
            if self.nowIn == "audio": stopwatch.restart_at(seek_time_secs)
            self.seeking = False

    def media_time_changed(self, _):
        length_milisec = self.player.get_length()
        time_milisec = self.player.get_time()
        self.position = time_milisec/1000
        remaining = (length_milisec - time_milisec)/1000
        duration = length_milisec/1000
        if self.seeking == False:
            GLib.idle_add(self.slider.set_range, 0, duration)
            GLib.idle_add(self.slider.set_value, self.position)
        fvalue, svalue = str(timedelta(seconds=round(self.position))), str(timedelta(seconds=int(remaining)))
        GLib.idle_add(self.label.set_text, fvalue)
        GLib.idle_add(self.label_end.set_text, svalue)

    def on_shuffBut_clicked(self, *_): self.neo_playlist_gen(name='shuffle')

    def nosub_hide(self, *_):
        self.nosub.hide()
        return True

    def on_act_sub(self, _, state):
        if state == True and self.nowIn == "video":
            filename = self.url.split("/")[-1]
            try: neo_tmpdbnow = os.listdir(self.url.replace(filename, "")+"misc/")
            except: neo_tmpdbnow = []
            tmpdbnow = os.listdir(self.url.replace(filename, ""))
            if os.path.splitext(filename)[0]+".srt" in tmpdbnow or os.path.splitext(filename)[0]+".srt" in neo_tmpdbnow:
                print("Subtitle found!")
                srfile = os.path.splitext(self.url)[0]+".srt"
                neo_srfile = self.url.replace(filename, "")+"misc/"+os.path.splitext(filename)[0]+".srt"
                print(srfile, neo_srfile)
                # if os.path.isfile(neo_srfile): self.player.video_set_subtitle_file(neo_srfile)
                # else: self.player.video_set_subtitle_file(srfile)
                try:
                    with open (srfile, 'r') as subfile: presub = subfile.read()
                except:
                    with open (neo_srfile, 'r') as subfile: presub = subfile.read()
                subtitle_gen = srt.parse(presub)
                subtitle = list(subtitle_gen)
                self.needSub = True
                subs = futures.ThreadPoolExecutor(max_workers=2)
                subs.submit(self.subShow, subtitle)
            else:
                self.nosub.set_title(self._("Subtitle file not found"))
                self.nosub.show_all()
                GLib.idle_add(self.subcheck.set_state, False)
                self.pause()
        else:
            # self.player.video_set_spu(-1)
            self.needSub = False

    def subShow(self, subtitle):
        while self.needSub == True:
            sleep(0.001)
            for line in subtitle:
                if self.position >= line.start.total_seconds() and self.position <= line.end.total_seconds():
                    GLib.idle_add(self.theTitle.set_markup, f"<span size='{int(self.size3)}' color='white'>{line.content}</span>")
                    self.theTitle.set_margin_bottom(self.size4)
                    GLib.idle_add(self.theTitle.show)
                    while self.needSub == True and self.position <= line.end.total_seconds() and self.position >= line.start.total_seconds():
                        sleep(0.001)
                        pass
                    GLib.idle_add(self.theTitle.hide)
                    GLib.idle_add(self.theTitle.set_label, "")

    def play(self, misc=""):
        if self.clickedE:
            self.url, self.nowIn = self.clickedE, self.useMode
            if self.useMode == "audio": self.player = self.audioPipe
            else: self.player = self.videoPipe
        elif "/" in misc:
            self.url, self.nowIn, self.player = misc, "video", self.videoPipe
            GLib.idle_add(self.subcheck.set_state, False)
        elif misc == "continue":
            if self.useMode == "audio":
                if self.audioPipe.get_state() == vlc.State.NothingSpecial or self.audioPipe.get_state() == vlc.State.Stopped: return
                self.player, self.nowIn = self.audioPipe, "audio"
            else:
                if self.videoPipe.get_state() == vlc.State.NothingSpecial or self.videoPipe.get_state() == vlc.State.Stopped: return
                self.player, self.nowIn = self.videoPipe, "video"
        else:
            stopwatch.stop()
            stopwatch.reset()
            try: self.url, self.nowIn, self.player = self.playlist[self.tnum]["uri"], "audio", self.audioPipe
            except: return
        print("Play")
        self.res, self.playing, self.position = True, True, 0
        if self.useMode == "audio":
            self.title = self.playlist[self.tnum]["title"]
            tools.themer(self.provider, self.window, self.rounded, self.color, self.tnum)
        if misc != "continue":
            # self.player.set_mrl(self.url)
            Media = self.vlcInstance.media_new(self.url)
            Media.add_options("no-sub-autodetect-file")
            # self.Media.add_options("freetype-rel-fontsize=500")
            self.player.set_media(Media)
        self.player.play()
        if self.nowIn == "audio": stopwatch.start()
        GLib.idle_add(self.header.set_subtitle, self.url.split("/")[-1])
        GLib.idle_add(self.plaicon.set_from_icon_name, "media-playback-pause", Gtk.IconSize.BUTTON)
        if self.useMode == "audio" and misc != "continue":
            ld_cov = futures.ThreadPoolExecutor(max_workers=1)
            ld_cov.submit(self.load_cover)

    def on_playBut_clicked(self, button):
        if self.plaicon.is_visible() == False: return
        if self.useMode == "audio" and self.nowIn != "video": self.adj.set_value(self.tnum*72-140)
        if self.nowIn == self.useMode or self.nowIn == "" or "/" in button:
            if not self.playing:
                if not self.res or "/" in str(button): self.play(button)
                else: self.resume()
            else: self.pause()
        else: self.play("continue")

    def on_main_delete_event(self, *_):
        self.force, self.stopKar, self.hardReset, self.needSub = True, True, True, False
        raise SystemExit
    
    def on_media(self, app, action):
        print(app, action)
        if app == "io.github.swanux.hbud" and self.url:
            if action == "Next": self.on_next("xy")
            elif action == "Previous": self.on_prev("xy")
            elif not self.playing: self.resume()
            elif self.playing: self.pause()
    
    def _sig_drag_drop(self, widget, *_): self.dst = int(widget.get_name().replace("trackbox_", ""))

    def _sig_drag_end(self, widget, _): self.reorderer(int(widget.get_name().replace("trackbox_", "")), self.dst)

    def reorderer(self, src, dst):
        playlistLoc, cutList = self.playlist, []
        if dst < src:
            [cutList.append(playlistLoc[i]) for i in range(dst, src+1)]
            rby, corrector = 1, dst
        elif dst > src:
            [cutList.append(playlistLoc[i]) for i in range(src, dst+1)]
            rby, corrector = -1, src
        cutList = deque(cutList)
        cutList.rotate(rby)
        cutList = list(cutList)
        for i in range(len(cutList)):
            self.playlist[i+corrector] = cutList[i]
        GLib.idle_add(self.neo_playlist_gen, "rename", src, dst)

    def on_key_local(self, _, key):
        # Add on_key as key_press signal to the ui file - main window preferably
        # print(key.keyval)
        if time() - self.key_time >= 0.05:
            self.key_time = time()
            try:
                if Gdk.ModifierType.CONTROL_MASK & key.state: # Ctrl combo
                    if key.keyval == 102: self.on_dropped("key")
                    elif key.keyval == 111: self.on_openFolderBut_clicked(None)
                elif key.keyval == 32 and self.url: self.on_playBut_clicked(0) # Space
                elif key.keyval == 65307 or key.keyval == 65480:
                    if self.useMode == "video": self.on_karaoke_activate(0) # ESC and F11
                elif key.keyval == 65363: self.on_next("") # Right
                elif key.keyval == 65361: self.on_prev("") # Left
                elif key.keyval == 65535 and self.useMode == "audio": # Delete
                    self.ednum = self.tnum
                    self.del_cur()
                elif key.keyval == 65362 and self.useMode == "audio": # Up
                    self.reorderer(self.tnum, self.tnum-1)
                elif key.keyval == 65364 and self.useMode == "audio": # Down
                    self.reorderer(self.tnum, self.tnum+1)
            except: pass

    def media_end_reached(self, _):
        if self.nowIn == "audio": self.on_next("xy")
        elif self.nowIn == "video": self.stop(True)

    def _on_size_allocated(self, *_):
        sleep(0.01)
        x, y = self.sub.get_size()
        self.size, self.size2 = 50*x, 21.4285714*x
    
    def _on_size_allocated0(self, *_):
        sleep(0.01)
        if self.needSub == True:
            x, y = self.window.get_size()
            self.size3, self.size4 = self.sSize*y, float(f"0.0{int(self.sMarg)}")*y

    def on_off_but_clicked(self, _):
        self.off_spin.update()
        self.offset = int(self.off_spin.get_value())
        f = MediaFile(self.playlist[self.tnum]["uri"])
        f.offset = self.offset
        f.save()
        self.sub.set_focus(None)

    def on_correct_lyr(self, _):
        if not os.path.isdir(f"{self.folderPath}/misc"):
            print("init")
            os.system(f"mkdir {self.folderPath}/misc")
        print(f"{self.folderPath}/misc/{self.tmp_tmp}.txt")
        f = open(f"{self.folderPath}/misc/{self.tmp_tmp}.txt", "w+")
        f.write(self.tmp_lyric)
        f.close()
        GLib.idle_add(self.substackhead.hide)
    
    def on_wrong_lyr(self, _): self.on_karaoke_activate()

    def on_karaoke_activate(self, *_):
        if self.useMode == "audio" and self.nowIn == "audio":
            if self.playing == True or self.res == True:
                print('Karaoke')
                self.stopKar = False
                track = self.playlist[self.tnum]["title"]
                try:
                    artist = self.playlist[self.tnum]["artist"].split("/")[0]
                    if artist == "AC": artist = self.playlist[self.tnum]["artist"]
                except: artist = self.playlist[self.tnum]["artist"]
                dbnow, neo_dbnow = [], []
                if self.clickedE:
                    folPathClick = self.clickedE.replace(self.clickedE.split("/")[-1], "")
                    tmpdbnow = os.listdir(folPathClick)
                else:
                    tmpdbnow = os.listdir(self.folderPath)
                    try: neo_tmpdbnow = os.listdir(self.folderPath+"/misc/")
                    except: neo_tmpdbnow = []
                for i in tmpdbnow:
                    if ".srt" in i or ".txt" in i:
                        x = i
                        if self.clickedE: dbnow.append(f"{folPathClick}{x}")
                        else: dbnow.append(f"{self.folderPath}/{x}")
                for i in neo_tmpdbnow:
                    if ".srt" in i or ".txt" in i:
                        x = i
                        neo_dbnow.append(f"{self.folderPath}/misc/{x}")
                self.sub.set_title(f'{track} - {artist}')
                tmp = os.path.splitext(self.playlist[self.tnum]["uri"])[0]
                neo_tmp = os.path.splitext(self.playlist[self.tnum]["uri"].split("/")[-1])[0]
                if f"{tmp}.srt" not in dbnow and f"{self.folderPath}/misc/{neo_tmp}.srt" not in neo_dbnow:
                    GLib.idle_add(self.off_but.hide)
                    GLib.idle_add(self.off_lab.hide)
                    GLib.idle_add(self.off_spin.hide)
                    if f"{tmp}.txt" in dbnow or f"{self.folderPath}/misc/{neo_tmp}.txt" in neo_dbnow:
                        try: f = open(f"{tmp}.txt", "r")
                        except: f = open(f"{self.folderPath}/misc/{neo_tmp}.txt", "r")
                        lyric = f.read()
                        f.close()
                        self.lyrLab.set_label(lyric)
                        self.subStack.set_visible_child(self.lyrmode)
                        self.sub.show_all()
                        GLib.idle_add(self.substackhead.hide)
                    else:
                        self.substackhead.set_visible_child(self.subbox2)
                        thread = futures.ThreadPoolExecutor(max_workers=2)
                        thread.submit(self.lyr_fetcher, artist, track, neo_tmp)
                else:
                    GLib.idle_add(self.off_but.show)
                    GLib.idle_add(self.off_lab.show)
                    GLib.idle_add(self.off_spin.show)
                    f = MediaFile(self.playlist[self.tnum]["uri"])
                    try:
                        field = MediaField(MP3DescStorageStyle(u'offset'), StorageStyle(u'offset'))
                        f.add_field(u'offset', field)
                    except: pass
                    if f.offset == None: f.offset = 0
                    self.offset = int(f.offset)
                    GLib.idle_add(self.off_spin.set_value, self.offset)
                    f.save()
                    print("FOUND")
                    try:
                        with open (f"{tmp}.srt", "r") as subfile: presub = subfile.read()
                    except:
                        with open (f"{self.folderPath}/misc/{neo_tmp}.srt", "r") as subfile: presub = subfile.read()
                    subtitle_gen = srt.parse(presub)
                    subtitle, lyrs = list(subtitle_gen), futures.ThreadPoolExecutor(max_workers=2)
                    lyrs.submit(self.slideShow, subtitle)
                    self.subStack.set_visible_child(self.karmode)
                    self.substackhead.set_visible_child(self.subbox)
                    self.sub.show_all()
        elif self.useMode == "video":
            if self.fulle == False:
                GLib.idle_add(self.karaokeIcon.set_from_icon_name, "view-restore", Gtk.IconSize.BUTTON)
                self.window.fullscreen()
                ld_clock = futures.ThreadPoolExecutor(max_workers=1)
                ld_clock.submit(self.clock)
            else:
                GLib.idle_add(self.karaokeIcon.set_from_icon_name, "view-fullscreen", Gtk.IconSize.BUTTON)
                self.resete, self.keepReset = False, False
                self.window.unfullscreen()
                self.mage()

    def lyr_fetcher(self, artist, track, tmp):
        GLib.idle_add(self.lyrStack.set_visible_child, self.lyrSpin)
        lyric = None
        if self.musixe == True and self.lyr_states[0] == True:
            lyric, self.lyr_states = musixapi.get_lyric(artist, track), [False, True, True]
        if self.letrase == True and lyric == None and self.lyr_states[1] == True:
            lyric, self.lyr_states = letrasapi.get_lyric(artist, track), [False, False, True]
        if self.azlyre == True and lyric == None and self.lyr_states[2] == True:
            lyric, self.lyr_states = tools.get_lyric(track, artist, self.DAPI), [False, False, False]
        GLib.idle_add(self.lyrStack.set_visible_child, self.karaokeBut)
        if lyric == 0:
            GLib.idle_add(tools.diabuilder, self._('Can not get correct lyrics for the current track. Please place the synced .srt file  or the raw .txt file alongside the audio file, with the same name as the audio file.'), self._("Information"), Gtk.MessageType.INFO, Gtk.ButtonsType.OK, self.window)
            ld_hide = futures.ThreadPoolExecutor(max_workers=1)
            ld_hide.submit(self.on_hide)
        else:
            self.tmp_lyric, self.tmp_tmp = lyric, tmp
            GLib.idle_add(self.lyrLab.set_label, lyric)
            GLib.idle_add(self.subStack.set_visible_child, self.lyrmode)
            GLib.idle_add(self.sub.show_all)

    def mouse_enter(self, *_):
        if self.fulle == True: self.keepReset = True
    
    def mouse_leave(self, *_):
        if self.fulle == True: self.keepReset = False
    
    def mage(self):
        GLib.idle_add(self.exBot.show)
        cursor = Gdk.Cursor.new_from_name(self.window.get_display(), 'default')
        self.window.get_window().set_cursor(cursor)

    def mouse_moving(self, *_):
        if self.fulle == True:
            self.resete = True
            if self.exBot.get_visible() == False:
                self.mage()
                ld_clock = futures.ThreadPoolExecutor(max_workers=1)
                ld_clock.submit(self.clock)

    def clock(self):
        start = time()
        while time() - start < 2:
            sleep(0.00001)
            if self.hardReset == True: return
            if self.keepReset == True: start = time()
            elif self.resete == True: start, self.resete = time(), False    
        if self.fulle == True:
            GLib.idle_add(self.exBot.hide)
            cursor = Gdk.Cursor.new_for_display(self.window.get_display(), Gdk.CursorType.BLANK_CURSOR)
            self.window.get_window().set_cursor(cursor)

    def on_state_change(self, _, event):
        if event.changed_mask & Gdk.WindowState.FULLSCREEN:
            self.fulle = bool(event.new_window_state & Gdk.WindowState.FULLSCREEN)
            print(self.fulle)

    def slideShow(self, subtitle):
        self.lenlist = len(subtitle)-1
        while not self.stopKar:
            self.line1, self.line2, self.line3, self.buffer = [], [], [], []
            self.hav1, self.hav2, self.hav3, self.where = False, False, False, -1
            for word in subtitle:
                if '#' in word.content:
                    self.buffer.append(word)
                    if not self.hav1: self.to1()
                    elif not self.hav2: self.to2()
                    else: self.to3()
                else: self.buffer.append(word)
                if self.stopKar or self.seekBack: break
                self.where += 1
            if not self.seekBack:
                self.to2()
                self.to1()
                self.line2 = []
                self.sync()
                self.stopKar = True
            else: self.seekBack = False
    
    def to1(self):
        if self.hav2: self.line1 = self.line2
        else:
            self.line1 = self.buffer
            self.buffer = []
        self.hav1 = True

    def to2(self):
        if self.where+1 <= self.lenlist:
            if self.hav3: self.line2 = self.line3
            else:
                self.line2 = self.buffer
                self.buffer = []
            self.hav2 = True
        else:
            if self.hav1 and not self.hav3: self.to1()
            self.line2 = self.line3
            self.line3 = []
            self.sync()

    def to3(self):
        if self.where+2 <= self.lenlist:
            if self.hav1 and self.hav3: self.to1()
            if self.hav2 and self.hav3: self.to2()
            self.line3 = self.buffer
            self.buffer, self.hav3 = [], True
        else:
            if self.hav1: self.to1()
            if self.hav2: self.to2()
            self.line3 = self.buffer
            self.buffer, self.hav3 = [], False
        self.sync()

    def sync(self):
        simpl2, simpl3 = "", ""
        if self.line2 != []:
            for z in self.line2:
                if self.stopKar or self.seekBack: break
                simpl2 += f"{z.content.replace('#', '')} "
        else: simpl2 = ""
        if self.line3 != []:
            for z in self.line3:
                if self.stopKar or self.seekBack: break
                simpl3 += f"{z.content.replace('#', '')} "
        else: simpl3 = ""
        GLib.idle_add(self.label2.set_markup, f"<span size='{int(self.size2)}'>{simpl2}</span>")
        GLib.idle_add(self.label3.set_markup, f"<span size='{int(self.size2)}'>{simpl3}</span>")
        done, tmpline, first, tl1, it = "", self.line1[:], True, self.line1, 1
        tl1.insert(0, "")
        maxit = len(tl1)-1
        for xy in tl1:
            if self.stopKar or self.seekBack: break
            if first: first = False
            else: tmpline = tmpline[1:]
            leftover = ""
            for y in tmpline:
                if self.stopKar or self.seekBack: break
                leftover += f"{y.content.replace('#', '')} "
            try: GLib.idle_add(self.label1.set_markup, f"<span size='{self.size}' color='green'>{done}</span> <span size='{self.size}' color='green'> {xy.content.replace('#', '')}</span> <span size='{self.size}'> {leftover}</span>")
            except: GLib.idle_add(self.label1.set_markup, f"<span size='{self.size}' color='green'>{done}</span> <span size='{self.size}' color='green'> {xy}</span> <span size='{self.size}'> {leftover}</span>")
            while not self.stopKar:
                sleep(0.01)
                if it > maxit:
                    if stopwatch.duration >= xy.end.total_seconds()+self.offset/1000 and stopwatch.duration >= 0.5: break
                else:
                    xz = tl1[it]
                    if stopwatch.duration >= xz.start.total_seconds()+self.offset/1000 and stopwatch.duration >= 0.5: break
                if self.seekBack: break
            it += 1
            try:
                if done == "": done += f"{xy.content.replace('#', '')}"
                else: done += f" {xy.content.replace('#', '')}"
            except: pass

    def config_write(self, *_):
        self.roundSpin.update()
        self.subSpin.update()
        self.subMarSpin.update()
        self.darke, self.color = self.dark_switch.get_state(), self.colorer.get_rgba().to_string()
        self.musixe, self.azlyre, self.letrase, self.cover_size = self.mus_switch.get_state(), self.az_switch.get_state(), self.letr_switch.get_state(), int(self.comboSize.get_active_id())
        self.rounded = self.roundSpin.get_value()
        self.sSize, self.sMarg = self.subSpin.get_value(), self.subMarSpin.get_value()
        parser.set('subtitles', 'margin', str(self.sMarg))
        parser.set('subtitles', 'size', str(self.sSize))
        parser.set('gui', 'rounded', str(self.rounded))
        parser.set('gui', 'dark', str(self.darke))
        parser.set('gui', 'color', self.color)
        parser.set('services', 'MusixMatch', str(self.musixe))
        parser.set('services', 'AZLyrics', str(self.azlyre))
        parser.set('services', 'Letras.br', str(self.letrase))
        parser.set('services', 'CoverSize', str(self.cover_size))
        file = open(confP, "w+")
        parser.write(file)
        file.close()
        self.settings.set_property("gtk-application-prefer-dark-theme", self.darke)
        tools.themer(self.provider, self.window, self.rounded, self.color, self.tnum)

    def on_hide(self, *_):
        self.stopKar = True
        self.lyr_states = [True, True, True]
        self.sub.hide()
        return True
    
    def on_key(self):
        Keybinder.init()
        Keybinder.bind("<Ctrl>space", self.on_playBut_clicked)

user, parser, confP, rounded, dark, color, musix, azlyr, letras, coverSize, sSize, sMarg = tools.real_init()
app = Main()
app.connect('activate', app.on_activate)
app.run(None)

# GTK_DEBUG=interactive
# to debug