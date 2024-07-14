# from gi.repository import GObject

# class ComboRow(GObject.Object):
#     __gtype_name__ = 'ComboRow'

#     def __init__(self, row_id: str, row_name: str):
#         super().__init__()

#         self._row_id = row_id
#         self._row_name = row_name

#     @GObject.Property
#     def row_id(self) -> str:
#         return self._row_id

#     @GObject.Property
#     def row_name(self) -> str:
#         return self._row_name

#     def add_combo_row(self, title: str, values: dict, callback=None, subtitle="") -> None:
#         if self._current_group == None:
#             return

#         combo = Adw.ComboRow()
#         combo.set_title(title)
#         combo.set_subtitle(subtitle)

#         # Jesus christ, why is this so complicated?
#         store = Gio.ListStore(item_type=ComboRow)
#         for value in values:
#             store.append(ComboRow(value, values[value]))

#         factory = Gtk.SignalListItemFactory()
#         factory.connect("setup", lambda factory,item : item.set_child(Gtk.Label()))
#         factory.connect("bind", lambda factory,item : item.get_child().set_text(item.get_item().row_name))

#         combo.set_model(store)
#         combo.set_factory(factory)

#         # TODO: connect callback function
#         if callback != None:
#             pass

#         self._current_group.add(combo)
