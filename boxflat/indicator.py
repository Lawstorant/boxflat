from gi.repository import Gio
from time import sleep

xml_content = None
with open("data/org.kde.StatusNotifierItem.xml", "r") as file:
    xml_content = file.read()

node_info = Gio.DBusNodeInfo.new_for_xml(xml_content)
interface_info = node_info.interfaces[0]

bus = Gio.bus_get_sync(Gio.BusType.SESSION)

bus_name="org.kde.StatusNotifierWatcher",
object_path="/StatusNotifierWatcher",
interface_name="org.kde.StatusNotifierWatcher",
method_name="RegisterStatusNotifierItem",
