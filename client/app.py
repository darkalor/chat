import wx
from client import Client


class App(wx.Frame):

    def __init__(self):
        self.app = wx.App()
        self.client = Client(self, 'localhost', 5000)

        user_dialog_box = wx.TextEntryDialog(None, "Login", "Username", "")
        if user_dialog_box.ShowModal() == wx.ID_OK:
            self.username = user_dialog_box.GetValue()

            # Set up the main window
            wx.Frame.__init__(self,
                              parent=None,
                              title="Python Chat 2000X: " + self.username,
                              size=(500, 400),
                              style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)

            vert_sizer = wx.BoxSizer(wx.VERTICAL)
            self.chatScreen = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY)
            self.messageBox = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER, size=(300, 25))
            self.messageBox.SetMaxLength(141)  # We're better than twitter

            vert_sizer.Add(self.chatScreen, 1, wx.EXPAND)
            vert_sizer.Add(self.messageBox, 0, wx.EXPAND)

            hor_sizer = wx.BoxSizer(wx.HORIZONTAL)
            self.userListScreen = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY)

            hor_sizer.Add(vert_sizer, flag=wx.EXPAND, border=10)
            hor_sizer.Add(self.userListScreen, 1, wx.EXPAND)

            self.SetSizer(hor_sizer)
            self.messageBox.Bind(wx.EVT_TEXT_ENTER, self.send)

            self.Bind(wx.EVT_CLOSE, self.on_close)

    def on_close(self, event):
        self.app.ExitMainLoop()

    def _display(self, message):
        char_text = self.chatScreen.GetValue()
        self.chatScreen.SetValue(char_text + message + "\n")

    def display(self, message):
        wx.CallAfter(self._display, message)

    def _show_users(self, user_list):
        users = "\n".join(user_list)
        self.userListScreen.SetValue(users)

    def show_users(self, user_list):
        wx.CallAfter(self._show_users, user_list)

    def send(self, event):
        message = self.messageBox.GetValue()
        char_text = self.chatScreen.GetValue()
        self.chatScreen.SetValue(char_text + "You: " + message + "\n")
        self.chatScreen.SetInsertionPointEnd()
        self.messageBox.SetValue("")
        try:
            self.client.send(message)
        except Exception as e:
            self.display("Failed to send")

    def run(self):
        self.client.setDaemon(True)
        self.client.start()
        self.Show()
        self.app.MainLoop()


# Instantiate and run
app = App()
app.run()