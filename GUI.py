from tkinter import Tk, Frame, Scrollbar, Label, END, Entry, Text, VERTICAL, Button, Toplevel,Listbox,SINGLE,MULTIPLE
import socket
import threading
from tkinter import messagebox
import os
import argparse

from datetime import datetime

class GUI:
    client_socket = None
    last_received_message = None

    def __init__(self, master,id):
        self.history_content=None
        self.root = master
        self.chat_transcript_area = None
        self.name_widget = None
        self.enter_text_widget = None
        self.join_button = None
        self.history_button=None
        self.userlist=""
        self.initialize_socket()
        self.initialize_gui()
        self.listen_for_incoming_messages_in_a_thread()
        self.select_history=None
        self.group_button=None
        self.searchKey=None
        

    def initialize_socket(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        parser=argparse.ArgumentParser()
        parser.add_argument('--id')
        args=parser.parse_args()
        id=args.id
        if(id!='n'):
            remote_ip = '127.0.0.1'
        else:
            remote_ip='127.0.0.2'
        print("REMOTE İP")
        print(remote_ip)
        remote_port = 10319
        self.client_socket.connect((remote_ip, remote_port))

    def initialize_gui(self):
        self.root.title("Socket Chat")
        self.root.geometry('800x600')
        self.root.resizable(0, 0)
        self.display_chat_box()
        self.display_name_section()
        self.display_chat_entry_box()
        self.onlineList()

    def onlineList(self):
        frame=Frame()
        index=1
        onlineUsers=Listbox(frame,selectmode=MULTIPLE)
        files=[]
        import os
        listElement='./Message History'
        files = os.listdir(listElement)
        for f in files:
            onlineUsers.insert(index,f)
            index=index+1
        onlineUsers.pack(side='left')
        self.group_button=Button(frame,text="Create Group",command= lambda: self.gui_thread(onlineUsers.curselection())).pack(side='right')
        frame.pack(side='bottom')
        
    def gui_thread(self,para):
        for t in para:
            os.system('start cmd /k "python GUI.py --id n"')
        
        
    def listen_for_incoming_messages_in_a_thread(self):
        thread = threading.Thread(target=self.receive_message_from_server, args=(self.client_socket,))
        thread.start()

    def receive_message_from_server(self, so):
        while True:
            buffer = so.recv(256)
            if not buffer:
                break
            message = buffer.decode('utf-8')
            if "joined" in message:
                user = message.split(":")[1]
                message = user + " has joined"
                self.chat_transcript_area.insert('end', message + '\n')
                self.chat_transcript_area.yview(END)
                self.userlist=self.userlist+user+"_"
                
            else:
                self.chat_transcript_area.insert('end', message + '\n')
                self.chat_transcript_area.yview(END)
            self.create_history(self.name_widget.get(),message)
        so.close()

    def create_history(self,user,message):
        now = datetime.now()
        date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
        path=("./Message History/"+user+"/")
        print(path)
        print("Uzantisini kaydedilen mesaj şudur")
        print(message)
        try:
            os.mkdir(path)
        except OSError:
           a=5
        else:
            a=4
        ###CREATİNG TEXT FİLE WİTH STORES STORY OF USER###
        message=message+" "
        try:
            history=open(path+self.userlist+".txt","a+")
            history.write(message)
            history.write(date_time)
            history.write("\n")
            history.close()
        except:
            history=open(path+self.userlist+".txt","w+")
            history.write(message)
            history.write(date_time)
            history.write("\n")
            history.close()

    def display_name_section(self):
        frame = Frame()
        Label(frame, text='Enter your name:', font=("Helvetica", 16)).pack(side='left', padx=10)
        self.name_widget = Entry(frame, width=50, borderwidth=2)
        self.name_widget.pack(side='left', anchor='e')
        self.join_button = Button(frame, text="Join", width=10, command=self.on_join).pack(side='left')
        self.history_button = Button(frame,text="Display History",width=10,command=self.display_history).pack()
        frame.pack(side='top', anchor='nw')

    def display_history(self):
        frame=Frame()
        newWindow = Toplevel(frame)
        index=1
        fileList=Listbox(newWindow,selectmode=SINGLE)
        files=[]
        import os
        listElement='./Message History/'+self.name_widget.get()
        files = os.listdir(listElement)
        for f in files:
            fileList.insert(index,f)
            index=index+1
        newWindow.geometry("500x200")
        fileList.pack(side='top')
        self.select_history = Button(newWindow, text="Select", width=10,command= lambda: self.print(fileList.get(fileList.curselection()))).pack()
   
    def print(self,text):
        username=self.name_widget.get()
        print(username)
        path='./Message History/'+username+'/'+text
        print(path)
        frame=Frame()
        newestWindow=Toplevel(frame)
        with open((path), "r") as f:
            self.history_content=Label(newestWindow, text=f.read()).pack()
        self.searchKey = Entry(newestWindow, width=50, borderwidth=2)
        self.searchKey.pack(side='left', anchor='e')
        self.searchButton=Button(newestWindow,text="Search",command=lambda: self.search(path)).pack()

    def search(self,path):
        frame=Frame()
        resultFrame=Toplevel(frame)
        result=Label(resultFrame)
        text=""
        with open(path, "r") as f:
            searchlines = f.readlines()
        for line in searchlines:
            if self.searchKey.get() in line:
                text=text+" "+line 
        result.config(text=text)
        result.pack()
                
    def display_chat_box(self):
        frame = Frame()
        Label(frame, text='Chat Box:', font=("Serif", 12)).pack(side='top', anchor='w')
        self.chat_transcript_area = Text(frame, width=60, height=10, font=("Serif", 12))
        scrollbar = Scrollbar(frame, command=self.chat_transcript_area.yview, orient=VERTICAL)
        self.chat_transcript_area.config(yscrollcommand=scrollbar.set)
        self.chat_transcript_area.bind('<KeyPress>', lambda e: 'break')
        self.chat_transcript_area.pack(side='left', padx=10)
        scrollbar.pack(side='right', fill='y')
        frame.pack(side='top')

    def display_chat_entry_box(self):
        frame = Frame()
        Label(frame, text='Enter message:', font=("Serif", 12)).pack(side='top', anchor='w')
        self.enter_text_widget = Text(frame, width=60, height=3, font=("Serif", 12))
        self.enter_text_widget.pack(side='left', pady=15)
        self.enter_text_widget.bind('<Return>', self.on_enter_key_pressed)
        frame.pack(side='top')

    def on_join(self):
        
        if len(self.name_widget.get()) == 0:
            messagebox.showerror(
                "Enter your name", "Enter your name to send a message")
            return
        self.name_widget.config(state='disabled')
        self.client_socket.send(("joined:" + self.name_widget.get()).encode('utf-8'))
        self.userlist=self.name_widget.get()+"_"

    def on_enter_key_pressed(self, event):
        if len(self.name_widget.get()) == 0:
            messagebox.showerror(
                "Enter your name", "Enter your name to send a message")
            return
        self.send_chat()
        self.clear_text()

    def clear_text(self):
        self.enter_text_widget.delete(1.0, 'end')

    def send_chat(self):
        senders_name = self.name_widget.get().strip() + ": "
        data = self.enter_text_widget.get(1.0, 'end').strip()
        message = (senders_name + data).encode('utf-8')
        self.chat_transcript_area.insert('end', message.decode('utf-8') + '\n')
        self.chat_transcript_area.yview(END)
       
       
        self.create_history(self.name_widget.get(),message.decode('utf-8'))
        self.client_socket.send(message)
        self.enter_text_widget.delete(1.0, 'end')
        return 'break'

    def on_close_window(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()
            self.client_socket.close()
            exit(0)


if __name__ == '__main__':
    root = Tk()
    gui = GUI(root,id)
    root.protocol("WM_DELETE_WINDOW", gui.on_close_window)
    root.mainloop()
