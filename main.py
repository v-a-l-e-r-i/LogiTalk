import threading
from socket import *

from customtkinter import *


class MainWindow(CTk):
   def __init__(self):
       super().__init__()
       self.geometry('400x300')

       self.frame = CTkFrame(self, width=200, height=self.winfo_height())
       self.frame.pack_propagate(False)
       self.frame.configure(width=0)
       self.frame.place(x=0, y=0)
       self.is_show_menu = False
       self.frame_width = 0

       self.label = CTkLabel(self.frame, text='Ваше Ім`я')
       self.label.pack(pady=30)
       self.entry = CTkEntry(self.frame)
       self.entry.pack()
       self.label_theme = CTkOptionMenu(self.frame, values=['Темна', 'Світла'], command=self.change_theme)
       self.label_theme.pack(side='bottom', pady=20)
       self.theme = None
       self.btn = CTkButton(self, text='▶', command=self.toggle_show_menu, width=30)
       self.btn.place(x=0, y=0)
       self.menu_show_speed = 20

       self.chat_text = CTkTextbox(self, state='disable')
       self.chat_text.place(x=0, y=30)

       self.message_input = CTkEntry(self, placeholder_text='Введіть повідомлення:')
       self.message_input.place(x=0, y=250)
       self.send_button = CTkButton(self, text='▶', width=40, height=30, command=self.send_message)
       self.send_button.place(x=200, y=250)

       self.username = self.entry.get()
       try:
           self.sock = socket(AF_INET, SOCK_STREAM)
           self.sock.connect(('localhost', 8080))
           hello = f"TEXT@{self.username}@[SYSTEM] {self.username} приєднався(лась) до чату!\n"
           self.sock.send(hello.encode('utf-8'))
           threading.Thread(target=self.recv_message, daemon=True).start()
       except Exception as e:
           self.add_message(f"Не вдалося підключитися до сервера: {e}")
       self.adaptive_ui()

   def toggle_show_menu(self):
       if self.is_show_menu:
           self.is_show_menu = False
           self.close_menu()
       else:
           self.is_show_menu = True
           self.show_menu()

   def show_menu(self):
       if self.frame_width <= 200:
           self.frame_width += self.menu_show_speed
           self.frame.configure(width=self.frame_width, height=self.winfo_height())
           if self.frame_width >= 30:
               self.btn.configure(width=self.frame_width, text='◀')
       if self.is_show_menu:
           self.after(20, self.show_menu)

   def close_menu(self):
       if self.frame_width >= 0:
           self.frame_width -= self.menu_show_speed
           self.frame.configure(width=self.frame_width)
           if self.frame_width >= 30:
               self.btn.configure(width=self.frame_width, text='▶')
       if not self.is_show_menu:
           self.after(20, self.close_menu)

   def change_theme(self, value):
       if value == 'Темна':
           set_appearance_mode('dark')
       else:
           set_appearance_mode('light')

   def adaptive_ui(self):
       self.chat_text.configure(width=self.winfo_width()-self.frame.winfo_width(), height=self.winfo_height()-self.message_input.winfo_height() - 30)
       self.chat_text.place(x=self.frame.winfo_width()-1)
       self.message_input.configure(width=self.winfo_width()-self.frame.winfo_width()-self.send_button.winfo_width())
       self.message_input.place(x=self.frame.winfo_width(), y=self.winfo_height()-self.send_button.winfo_height())
       self.send_button.place(x=self.winfo_width()-self.send_button.winfo_width(), y=self.winfo_height()-self.send_button.winfo_height())
       self.after(20, self.adaptive_ui)

   def add_message(self, text):
       self.username = self.entry.get()
       self.chat_text.configure(state='normal')
       self.chat_text.insert(END, f' {self.username}: {text}\n')
       self.chat_text.configure(state='disable')

   def send_message(self):
       message = self.message_input.get()
       if message:
           self.add_message(f"{self.username}: {message}")
           data = f"TEXT@{self.username}@{message}\n"
           try:
               self.sock.sendall(data.encode())
           except:
               pass
       self.message_input.delete(0, END)

   def recv_message(self):
       buffer = ""
       while True:
           try:
               chunk = self.sock.recv(4096)
               if not chunk:
                   break
               buffer += chunk.decode()

               while "\n" in buffer:
                   line, buffer = buffer.split("\n", 1)
                   self.handle_line(line.strip())
           except:
               break
       self.sock.close()

   def handle_line(self, line):
       if not line:
           return
       parts = line.split("@", 3)
       msg_type = parts[0]

       if msg_type == "TEXT":
           if len(parts) >= 3:
               author = parts[1]
               message = parts[2]
               self.add_message(f"{author}: {message}")
       elif msg_type == "IMAGE":
           if len(parts) >= 4:
               author = parts[1]
               filename = parts[2]

               self.add_message(f"{author} надіслав(ла) зображення: {filename}")

       else:
           self.add_message(line)

win = MainWindow()
win.mainloop()
