import wx
from client import Client
from threading import Lock

class App(wx.Frame):

    def __init__(self):

        self.app = wx.App()
        self.client = Client(self, 'localhost', 5000)

        # Set up the main window
        wx.Frame.__init__(self,
                          parent=None,
                          title='wxPython Example',
                          size=(500, 400),
                          style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.chatScreen = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.messageBox = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER, size=(300, 25))

        sizer.Add(self.chatScreen, 5, wx.EXPAND)
        sizer.Add(self.messageBox, 0, wx.EXPAND)
        self.SetSizer(sizer)
        self.messageBox.Bind(wx.EVT_TEXT_ENTER, self.send)
        self.lock = Lock()

    def get_chat_screen(self):
        with self.lock:
            chatScreen = self.chatScreen.GetValue()
        return chatScreen

    def set_chat_screen(self, message):
        with self.lock:
            self.chatScreen.SetValue(message)

    def _display(self, message):
        chatText = self.get_chat_screen()
        self.set_chat_screen(chatText + message + "\n")

    def display(self, message):
        wx.CallAfter(self._display, message)

    def send(self, event):
        message = self.messageBox.GetValue()
        chatText = self.get_chat_screen()
        self.set_chat_screen(chatText + message + "\n")
        self.chatScreen.SetInsertionPointEnd()
        self.messageBox.SetValue("")
        try:
            self.client.send(message)
        except Exception as e:
            self.display("Failed to send")

    def run(self):
        self.client.start()
        self.Show()
        self.app.MainLoop()


# Instantiate and run
app = App()
app.run()