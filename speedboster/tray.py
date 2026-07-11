#!/usr/bin/env python3
"""SpeedBoster: a simple tray app to monitor CPU/GPU temps and set fan speed."""
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

        slider_item = Gtk.MenuItem()
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        box.set_border_width(6)
        box.pack_start(Gtk.Label(label="Fan"), False, False, 0)
        self.slider = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 5)
        self.slider.set_value(50)
        self.slider.set_size_request(140, -1)
        self.slider.connect("value-changed", self.on_slider_changed)
        box.pack_start(self.slider, True, True, 0)
        slider_item.add(box)
        self.menu.append(slider_item)

        self.lock_item = Gtk.CheckMenuItem(label="Lock fan speed")
        self.lock_item.connect("toggled", self.on_lock_toggled)
        self.menu.append(self.lock_item)

        self.menu.append(Gtk.SeparatorMenuItem())

        quit_item = Gtk.MenuItem(label="Quit")
        quit_item.connect("activate", Gtk.main_quit)
        self.menu.append(quit_item)

        self.menu.show_all()
        self.indicator.set_menu(self.menu)

        GLib.timeout_add(REFRESH_MS, self.refresh)
        self.refresh()

    def on_lock_toggled(self, widget):
        try:
            if widget.get_active():
                fan.set_speed(self.slider.get_value())
            else:
                fan.set_auto()
        except fan.FanControlError as exc:
            self.show_error(str(exc))

    def on_slider_changed(self, widget):
        if self.lock_item.get_active():
            try:
                fan.set_speed(widget.get_value())
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
        return True


def main():
    SpeedBoosterApp()
    Gtk.main()


if __name__ == "__main__":
    main()
