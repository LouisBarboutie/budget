import tkinter as tk


class DateEntry(tk.Entry):
    def __init__(self, master: tk.Misc = None, **kwargs):
        super().__init__(master, **kwargs)
        self.placeholder = "DD/MM/YYYY"
        self.insert(0, self.placeholder)
        self.bind("<FocusIn>", self.on_focus)
        self.bind("<Key>", self.on_keypress)

    def on_keypress(self, event: tk.Event):
        pos = self.index(tk.INSERT)

        if event.keysym == "BackSpace":
            if pos > 0:
                self.delete(pos - 1, pos)
                self.insert(pos - 1, self.placeholder[pos - 1])

                if self.placeholder[pos - 2] == "/":
                    pos -= 1
                self.icursor(pos - 1)

            return "break"

        if event.keysym == "Delete":
            if pos < len(self.placeholder):
                self.delete(pos, pos + 1)
                self.insert(pos, self.placeholder[pos])

                if pos + 2 < len(self.placeholder) and self.placeholder[pos + 1] == "/":
                    pos += 1
                self.icursor(pos + 1)

            return "break"

        if event.char.isdigit():
            if pos < len(self.placeholder):
                self.delete(pos, pos + 1)
                self.insert(pos, event.char)

                next = pos + 1
                if next < len(self.placeholder):
                    if self.get()[next] == "/":
                        next += 1
                    self.icursor(next)

            return "break"

        if event.keysym not in ("Left", "Right"):
            return "break"

    def on_focus(self, event: tk.Event):
        self.icursor(0)
