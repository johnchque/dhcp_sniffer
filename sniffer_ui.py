import gi
import pymysql
from gi.repository import Gtk, Gio
from time import gmtime, strftime
gi.require_version('Gtk', '3.0')

conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='r00t')
cur = conn.cursor()


class TreeViewFilterWindow(Gtk.Window):

    def __init__(self):
        # Creating the window.
        Gtk.Window.__init__(self, title="DHCP sniffer")
        self.set_border_width(10)
        self.grid = Gtk.Grid()
        self.grid.set_column_homogeneous(True)
        self.grid.set_row_homogeneous(True)
        self.add(self.grid)

        # Creating the ListStore and filters.
        self.address_list_store = Gtk.ListStore(int, str, str, str)
        self.current_filter_time = None
        self.timeFilter = self.address_list_store.filter_new()

        # Adding the headers to the table list.
        self.treeview = Gtk.TreeView.new_with_model(self.timeFilter)
        for i, column_title in enumerate(["Id", "Identificador", "Direccion MAC", "IP"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            self.treeview.append_column(column)

        # Creating buttons for filtering time and their click functions.
        self.buttons = list()
        for time in ["Minuto", "Hora", "Todos"]:
            button = Gtk.Button(time)
            self.buttons.append(button)
            button.connect("clicked", self.on_selection_button_clicked)

        # Setting up the layout, putting the treeview in a scrollwindow, and the buttons in a row
        self.scrollable_treelist = Gtk.ScrolledWindow()
        self.scrollable_treelist.set_vexpand(True)
        self.grid.attach(self.scrollable_treelist, 0, 0, 8, 10)
        self.grid.attach_next_to(self.buttons[0], self.scrollable_treelist, Gtk.PositionType.TOP, 1, 1)
        for i, button in enumerate(self.buttons[1:]):
            self.grid.attach_next_to(button, self.buttons[i], Gtk.PositionType.RIGHT, 1, 1)
        self.scrollable_treelist.add(self.treeview)
        self.amount = Gtk.Label("Conexiones: 0")
        self.grid.attach_next_to(self.amount, self.scrollable_treelist, Gtk.PositionType.BOTTOM, 1, 1)

        self.show_all()

    def on_selection_button_clicked(self, widget):
        # Set the time to be checked.
        self.address_list_store.clear()
        self.current_filter_time = widget.get_label()
        print("%s selected!" % self.current_filter_time)
        # Get the data to display.
        conn.commit()
        cur.execute("USE sniffer")
        query = "SELECT id,name,mac,ip FROM data"
        if self.current_filter_time == "Minuto":
            second = strftime("%S", gmtime())
            minute = int(strftime("%M", gmtime())) - 1
            hour = strftime("%H", gmtime())
            query += " WHERE time < '" + hour + ":" + str(minute) + ":" + second + "'"
        elif self.current_filter_time == "Hora":
            second = strftime("%S", gmtime())
            minute = strftime("%M", gmtime())
            hour = int(strftime("%H", gmtime())) - 1
            query += " WHERE time < '" + str(hour) + ":" + minute + ":" + second + "'"

        # Add amount of connections
        number = cur.execute(query)
        self.amount.set_text("Conexiones: " + str(number))

        # Fetch all addresses
        addresses = cur.fetchall()
        for address in addresses:
            self.address_list_store.append(list(address))
        self.timeFilter.refilter()

win = TreeViewFilterWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
