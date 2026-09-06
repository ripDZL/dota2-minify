"Text waterfall"

import time

import dearpygui.dearpygui as dpg
from core import base, output, utils

from ui import shared

wrap_size = base.main_window_width - 10


def get_text():
    """Return the currently rendered activity log as plain text."""
    lines = []
    if base.HEADLESS:
        return ""

    for item in shared.terminal_history:
        item_id = item.get("id")
        if item_id is None or not dpg.does_item_exist(item_id):
            continue
        value = dpg.get_value(item_id)
        if value is not None:
            lines.append(str(value))
    return "\n".join(lines)


def copy_all(sender=None, app_data=None, user_data=None):
    """Copy the complete visible activity log to the system clipboard."""
    if base.HEADLESS:
        return
    dpg.set_clipboard_text(get_text())


def _copy_window_size():
    client_width_fn = getattr(dpg, "get_viewport_client_width", None)
    client_height_fn = getattr(dpg, "get_viewport_client_height", None)
    width = int(client_width_fn() if client_width_fn else dpg.get_viewport_width())
    height = int(client_height_fn() if client_height_fn else dpg.get_viewport_height())
    dialog_width = max(520, min(900, width - 80))
    dialog_height = max(320, min(640, height - 80))
    position = (max(20, (width - dialog_width) // 2), max(20, (height - dialog_height) // 2))
    return dialog_width, dialog_height, position


def show_copy_view(sender=None, app_data=None, user_data=None):
    """Open a selectable read-only view for copying individual log text."""
    if base.HEADLESS:
        return

    text = get_text()
    width, height, position = _copy_window_size()
    if not dpg.does_item_exist("activity_log_copy_window"):
        with dpg.window(
            tag="activity_log_copy_window",
            label="Activity Log",
            width=width,
            height=height,
            pos=position,
            no_saved_settings=True,
            no_collapse=True,
        ):
            dpg.add_text("Select any text below and press Ctrl+C, or copy the full log.")
            dpg.add_input_text(
                tag="activity_log_copy_text",
                default_value=text,
                multiline=True,
                readonly=True,
                width=-1,
                height=-58,
            )
            with dpg.group(horizontal=True):
                dpg.add_button(label="COPY ALL", callback=copy_all, width=100)
                dpg.add_button(
                    label="CLOSE",
                    callback=lambda: dpg.configure_item("activity_log_copy_window", show=False),
                    width=84,
                )
    else:
        dpg.set_value("activity_log_copy_text", text)
        dpg.configure_item(
            "activity_log_copy_window",
            width=width,
            height=height,
            pos=position,
            show=True,
        )

    dpg.focus_item("activity_log_copy_text")


@utils.ignore_if_headless
def scroll_to_end():
    time.sleep(0.05)
    dpg.set_y_scroll("terminal_window", dpg.get_y_scroll_max("terminal_window"))


def add_text(text_or_id, *args, msg_type: str | None = None, **kwargs):
    from ui import localization

    if text_or_id.startswith("&"):
        text = localization.localization_dict.get(text_or_id.replace("&", ""), text_or_id)
    else:
        text = text_or_id

    if args:
        text = text.format(*args)

    if msg_type is not None:
        if msg_type == "error":
            color = (255, 0, 0)
        elif msg_type == "warning":
            color = (255, 255, 0)
        elif msg_type == "success":
            color = (0, 255, 0)
        else:
            color = (0, 230, 230)
        kwargs["color"] = color

    if not base.HEADLESS and dpg.does_item_exist("terminal_window"):
        item = dpg.add_text(default_value=text, parent="terminal_window", wrap=wrap_size, indent=10, **kwargs)
        shared.terminal_history.append({"id": item, "key": text_or_id.replace("&", ""), "args": args})
        scroll_to_end()
        return item
    else:
        print(text)
        return None


def add_seperator():
    if not base.HEADLESS and dpg.does_item_exist("terminal_window"):
        dpg.add_separator(parent="terminal_window")
    else:
        print("-" * 50)


def clean():
    if not base.HEADLESS and dpg.does_item_exist("terminal_window"):
        dpg.delete_item("terminal_window", children_only=True)
    shared.terminal_history.clear()
    if not base.HEADLESS and dpg.does_item_exist("activity_log_copy_text"):
        dpg.set_value("activity_log_copy_text", "")


if not base.HEADLESS:
    output.register_output_callback(add_text)
    output.register_separator_callback(add_seperator)
    output.register_clean_callback(clean)
