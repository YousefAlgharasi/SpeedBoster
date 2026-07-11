#!/usr/bin/env python3
"""SpeedBoster: a simple tray app to monitor CPU/GPU temps and set fan mode."""
import gi

gi.require_version("Gtk", "3.0")
gi.require_version("AppIndicator3", "0.1")
from gi.repository import AppIndicator3, GLib, Gtk

from speedboster import fan, sensors

APP_ID = "speedboster"
REFRESH_MS = 2000


class SpeedBoosterApp:
    def __init__(self):
        self.indicator = AppIndicator3.Indicator.new(
            APP_ID, "sensors-temperature", AppIndicator3.IndicatorCategory.APPLICATION_STATUS
        )
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)

        self.menu = Gtk.Menu()

        self.temp_item = Gtk.MenuItem(label="CPU: -- °C   GPU: -- °C")
        self.temp_item.set_sensitive(False)
        self.menu.append(self.temp_item)

        self.menu.append(Gtk.SeparatorMenuItem())

        self._updating = False
        self.mode_items = {}
        for mode in fan.MODES:
            item = Gtk.RadioMenuItem.new_with_label_from_widget(
                next(iter(self.mode_items.values()), None), mode.capitalize()
            )
            item.connect("toggled", self.on_mode_toggled, mode)
            self.menu.append(item)
            self.mode_items[mode] = item

        self.menu.append(Gtk.SeparatorMenuItem())

        self.boost_item = Gtk.CheckMenuItem(label="Cooler Boost")
        self.boost_item.connect("toggled", self.on_boost_toggled)
        self.menu.append(self.boost_item)

        self.menu.append(Gtk.SeparatorMenuItem())

        quit_item = Gtk.MenuItem(label="Quit")
        quit_item.connect("activate", Gtk.main_quit)
        self.menu.append(quit_item)

        self.menu.show_all()
        self.indicator.set_menu(self.menu)

        GLib.timeout_add(REFRESH_MS, self.refresh)
        self.refresh()

    def on_mode_toggled(self, widget, mode):
        if self._updating or not widget.get_active():
            return
        try:
            fan.set_mode(mode)
        except fan.FanControlError as exc:
            self.show_error(str(exc))

    def on_boost_toggled(self, widget):
        if self._updating:
            return
        try:
            fan.set_cooler_boost(widget.get_active())
        except fan.FanControlError as exc:
            self.show_error(str(exc))

    def show_error(self, message):
        dialog = Gtk.MessageDialog(
            flags=0, message_type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.OK, text=message
        )
        dialog.run()
        dialog.destroy()

    def refresh(self):
        cpu = sensors.read_cpu_temp()
        gpu = sensors.read_gpu_temp()
        cpu_str = f"{cpu:.0f}°C" if cpu is not None else "--"
        gpu_str = f"{gpu:.0f}°C" if gpu is not None else "--"
        self.temp_item.set_label(f"CPU: {cpu_str}   GPU: {gpu_str}")

        if fan.available():
            try:
                state = fan.status()
                self._updating = True
                item = self.mode_items.get(state["fan_mode"])
                if item is not None:
                    item.set_active(True)
                self.boost_item.set_active(state["cooler_boost"])
            except fan.FanControlError:
                pass
            finally:
                self._updating = False

        return True


def main():
    SpeedBoosterApp()
    Gtk.main()


if __name__ == "__main__":
    main()
