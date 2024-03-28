# Copyright (C) 2024 OpenVision
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this
# program.  If not, see <https://www.gnu.org/licenses/>.

import tkinter as tk
import cv2
from PIL import Image, ImageTk
import mysql.connector
from tkinter import ttk, messagebox
import subprocess
import customtkinter as ctk
from tkcalendar import Calendar


class App(ctk.CTk):
    def __init__(self, window, window_title, video_source=0):
        super().__init__()
        self.window = window

        self.window.geometry("900x450")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)
        
        # Create a variable to store the selected option
        self.var = tk.StringVar()
        self.var.set("1")
        # Create the radio buttons
        radio_button1 = tk.Radiobutton(window, text="HD", variable=self.var, value="1")
        radio_button2 = tk.Radiobutton(window, text="FHD", variable=self.var, value="2")
        radio_button3 = tk.Radiobutton(window, text="QHD", variable=self.var, value="3")

        # Configure the command to be executed when a radio button is selected
        radio_button1.config(command=self.show_selection)
        radio_button2.config(command=self.show_selection)
        radio_button3.config(command=self.show_selection)

        # Pack the radio buttons into the window
        radio_button1.grid(row=3, column=1, pady=20, padx=0)
        radio_button2.grid(row=3, column=2, pady=20, padx=0)
        radio_button3.grid(row=3, column=3, pady=20, padx=0)
        #self.checkbox = ctk.CTkCheckBox(master=self.window)
        #self.checkbox.grid(row=3, column=0, pady=20, padx=20, sticky="n")
        #self.checkbox.configure(text="HD")
        #self.checkbox.select()

        ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
        ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

        # create database connection and cursor
        self.conn = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    passwd="password",
                    database="CameraDB"
                    )
        self.c = self.conn.cursor()


        # create treeview to display database
        self.treeview = tk.ttk.Treeview(self.window, columns=("Date", "Time", "Duration"))
        self.treeview.heading("#0", text="ID")
        self.treeview.heading("Date", text="Date")
        self.treeview.heading("Time", text="Time")
        self.treeview.heading("Duration", text="Duration")
        self.treeview.grid(row=0, column=0, padx=20, columnspan=12,  pady=(20, 10))

        # add entries to treeview
        self.add_entries()

        # create button to add entry
        self.add_button = tk.Button(self.window, text="Add Entry", command=self.add_entry_window)
        self.add_button.grid(row=1, column=1, pady=(20, 10))
        self.delete_button = tk.Button(self.window, text="Delete Entry", command=self.delete_entry)
        self.delete_button.grid(row=1, column=2, pady=(20, 10))
        self.edit_button = tk.Button(self.window, text="Edit Entry", command=self.edit_entry)
        self.edit_button.grid(row=1, column=3, pady=(20, 10))
        
        self.edit_button.config(state='disabled')
        
        # create a button that opens a new window with the camera feed
        self.btn2 = tk.Button(self.window, text="Open Camera Window", command=self.open_camera_window)
        self.btn2.grid(row=2, column=0, padx=20, pady=(20, 10))

        self.window.title(window_title)

        # Bind the close event to the window
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        # Set a flag to check if the video feed is running
        self.is_running = False

        # Start the tkinter mainloop
        self.window.mainloop()
    
    def show_selection(self):
        selected_option = self.var.get()
        print("Selected option:", selected_option)
        
    def open_camera_window(self):
        # create a new window with the camera feed
        self.camera_window = tk.Toplevel(self.window)
        self.camera_window.title("Camera Window")

        # Bind the close event to the window
        self.camera_window.protocol("WM_DELETE_WINDOW", self.cam_close)

        # create a label to display the camera feed
        label = tk.Label(self.camera_window)
        label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # initialize the camera capture
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 1920)
        self.cap.set(4, 1080)
        self.cap.set(cv2.CAP_PROP_FPS, 15)
        screen_width = 750  # Example screen width
        screen_height = 360  # Example screen height
        

        #tilt = self.checkbox.get()

        # update the label with each new frame from the camera
        def update_frame():
            ret, frame = self.cap.read()
            resized_frame = cv2.resize(frame, (screen_width, screen_height))
            
            if ret:
                # convert the frame to PIL format and display it on the label
                img = Image.fromarray(cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB))
                imgtk = ImageTk.PhotoImage(image=img)
                label.imgtk = imgtk
                label.configure(image=imgtk)
            label.after(10, update_frame)

        # start updating the label with new frames
        update_frame()

    def add_entries(self):
        # clear existing entries from treeview
        for i in self.treeview.get_children():
            self.treeview.delete(i)
        
        self.c.execute("SELECT * FROM CameraSchedule")
        rows = self.c.fetchall()
        
        # query database and add entries to treeview
        for row in rows:
            self.treeview.insert('', 'end', text=row[0], values=(row[1], row[2], row[3]))

    def add_entry(self,date, time, duration):
        # insert new entry into database
        self.c.execute("INSERT INTO CameraSchedule (Date, Time, Duration) VALUES (%s, %s, %s)", (date, time, duration))
        self.conn.commit()

        # update treeview
        self.add_entries()

    def add_entry_window(self):
        # create new window for adding an entry
        self.new_window = tk.Toplevel(self.window)
        self.new_window.title("Add Entry")
        
        def select_date():
            selected_date = cal.get_date()
            date_entry.delete(0, tk.END)
            date_entry.insert(0, selected_date)
            

        root = tk.Tk()
        root.title("Date Picker Example")

        cal = Calendar(root, selectmode="day", date_pattern="yyyy-mm-dd")
        cal.pack(pady=20)

        select_button = tk.Button(root, text="Select Date", command=select_date)
        select_button.pack(pady=10)
        
        # create entry fields for self.new_window        
        date_label = tk.Label(self.new_window, text="Date:")
        date_label.grid(row=0, column=0)
        date_entry = tk.Entry(self.new_window)
        date_entry.grid(row=0, column=1)
        

        time_label = tk.Label(self.new_window, text="Time:")
        time_label.grid(row=1, column=0)
        # Generate time values in 15-minute increments
        times = []
        for hour in range(5, 21):
            for minute in range(0, 60, 15):
                time = f"{hour:02d}{minute:02d}"
                times.append(time)

        self.time_entry = ttk.Combobox(self.new_window, textvariable=tk.StringVar())
        self.time_entry['values'] = times
        self.time_entry.grid(row=1, column=1)
        
        duration_label = tk.Label(self.new_window, text="Duration:")
        duration_label.grid(row=2, column=0)
        duration_entry = ttk.Combobox(self.new_window, textvariable=tk.StringVar())
        duration_entry['values'] = list(range(15, 181, 15))
        duration_entry.grid(row=2, column=1)
        
        
        # create button to add entry to database
        add_button = tk.Button(self.new_window, text="Add",
                               command=lambda: self.add_entry(date_entry.get(), self.time_entry.get(), duration_entry.get()))
        add_button.grid(row=3, column=1)
        
    def delete_entry(self):
        selected_item = self.treeview.focus()  # Get the currently selected item
        if selected_item:  # If an item is selected
            value = self.treeview.item(selected_item)['text']  # Retrieve the value of the first column
            print(value)  # Do something with the value
            self.treeview.delete(selected_item)  # Delete the selected item
        # Delete entry from database
        self.c.execute("DELETE FROM CameraSchedule WHERE ID = (%s)", (value,))
        self.conn.commit()
        
    def edit_entry(self):
        selected_item = self.treeview.focus()  # Get the currently selected item
        if selected_item:  # If an item is selected
            values = self.treeview.item(selected_item)['values']  # Retrieve the value of the first column
            #self.time_entry.insert(0, values[1])
            self.time_entry.current(values.index(default_value))
            _id = self.treeview.item(selected_item)['text']
            print(values)  # Do something with the value
            #self.treeview.delete(selected_item)  # Delete the selected item
            add_entry_window()
    
    def on_close(self):
        self.window.destroy()
        exit()

    def cam_close(self):
        self.cap.release()
        self.camera_window.destroy()


# Create the App object with the window title and video source
if __name__ == "__main__":
    app = App(ctk.CTk(), "USB Camera Feed")
    app.mainloop()

