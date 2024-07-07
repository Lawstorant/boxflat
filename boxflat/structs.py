from gi.repository import GObject

PICKER_COLORS = 8

class ComboRow(GObject.Object):
    __gtype_name__ = 'ComboRow'

    def __init__(self, row_id: str, row_name: str):
        super().__init__()

        self._row_id = row_id
        self._row_name = row_name

    @GObject.Property
    def row_id(self) -> str:
        return self._row_id

    @GObject.Property
    def row_name(self) -> str:
        return self._row_name
