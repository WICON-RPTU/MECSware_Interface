import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedStyle
import subprocess
import threading
import json
from PIL import Image, ImageTk

# Global variables to store the retrieved values
frequency_value = ""
bandwidth_value = ""
power_value = ""

# Create a list of options for each combobox
freq_options = ["3700", "3705", "3710", "3715"]
bw_options = ["5", "10", "15", "20"]
ratio_options = ["5:5", "7:3", "4:1"]
power_options = ["10", "12", "14", "16", "18", "20"]

# Create a style for bold text
bold_font = ('TkDefaultFont', 12, 'bold')
Entries_bold_font = ('TkDefaultFont', 10, 'bold')


# Create the main window
root = tk.Tk()
root.title("MECSware Interface")
root.geometry("800x600")  # Initial size of the window

# Set the theme for the application
style = ThemedStyle(root)
style.set_theme("adapta")  # Replace "adapta" with your desired theme

# Configure the main grid to be resizable
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

# Create the main frame with padding
frame = ttk.Frame(root, padding="20")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
frame.columnconfigure(0, weight=1)  # Allow horizontal expansion
frame.columnconfigure(1, weight=1)  # Allow horizontal expansion
frame.columnconfigure(2, weight=1)  # Allow horizontal expansion
frame.columnconfigure(3, weight=1)  # Allow horizontal expansion
frame.columnconfigure(4, weight=1)  # Allow horizontal expansion
frame.columnconfigure(5, weight=1)  # Allow horizontal expansion
frame.columnconfigure(6, weight=1)  # Allow horizontal expansion
frame.columnconfigure(7, weight=1)  # Allow horizontal expansion



def clear_console():
    """Clears the console."""
    output_text.delete("1.0", tk.END)

def send_command_message():
    """Displays a message indicating the command is being sent."""
    output_text.insert(tk.END, "Sending command... Waiting for confirmation.\n")

def trigger_terminal_command_submit_data():
    """Function to trigger the submission of terminal command and clear the console."""
    clear_console()
    send_command_message()
    threading.Thread(target=execute_put_command).start()

def execute_put_command():
    """Function to execute a PUT command using the entered parameters."""
    try:
        ip_address = ip_entry.get()
        port = port_entry.get()
        frequency = freq_combobox.get()
        bandwidth = bw_combobox.get()
        ratio = ratio_combobox.get()
        power = power_combobox.get()

        command = (
            f"curl -X PUT https://{ip_address}:{port}/5g/bs/conf -k -u admin:admin -d "
            f"'{{\"Name\": \"BS-114\", \"ID\": \"14\", \"Band\": \"78\", \"Bandwidth\": \"{bandwidth}\", "
            f"\"Frequency\": \"{frequency}\", \"Ratio\": \"{ratio}\", \"Power\": \"{power}\", \"Sync\": \"free\"}}' "
            f"-H \"Content-Type: application/json\" -v"
        )

        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = result.stdout

        output_text.after(0, output_text.delete, "end-2l", "end-1l")
        output_text.after(0, output_text.insert, tk.END, output)

        if "data received" in output.lower():
            output_text.after(0, output_text.delete, "1.0", tk.END)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def ping_test():
    """Function to execute a ping test to the provided IP address."""
    try:
        ip_address = ip_entry.get()
        clear_console()
        result = subprocess.run(['ping', '-c', '1', ip_address], capture_output=True, text=True)
        output_text.insert(tk.END, result.stdout)

        if result.returncode == 0:
            messagebox.showinfo("Ping Result", "Ping successful!")
        else:
            messagebox.showerror("Ping Result", "Ping failed!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def submit_command():
    """Function to submit a command and show a confirmation message."""
    trigger_terminal_command_submit_data()
    messagebox.showinfo("Command Result", "Terminal command executed successfully.")

def ping_command():
    """Function to start the ping test in a separate thread."""
    threading.Thread(target=ping_test).start()

def show_waiting_message():
    """Function to display a waiting message in the console."""
    clear_console()
    output_text.insert(tk.END, "Waiting for response from server...\n")
    output_text.see(tk.END)
    output_text.update_idletasks()

def get_current_data():
    """Function to get the current data from the server."""
    global frequency_value, bandwidth_value, power_value

    try:
        ip_address = ip_entry.get()
        port = port_entry.get()
        name = name_entry.get()

        command = (
            f"curl -X GET https://{ip_address}:{port}/5g/bs/status/{name} -k -u admin:admin "
            f"-H \"Content-Type: application/json\" -v"
        )

        show_waiting_message()
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = result.stdout

        output_text.after(0, output_text.delete, "end-2l", "end-1l")
        output_text.after(0, output_text.insert, tk.END, output)

        data = json.loads(output)
        frequency_value = data.get("frequency", "")
        bandwidth_value = data.get("bandwidth", "")
        power_value = data.get("tx_power", "")

        frequency_label.config(text=f"{frequency_value}")
        bandwidth_label.config(text=f"{bandwidth_value}")
        power_label.config(text=f"{power_value}")

        messagebox.showinfo("Current Data", f"Frequency: {frequency_value}\nBandwidth: {bandwidth_value}\nPower: {power_value}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def execute_command():
    """Function to execute an arbitrary command."""
    try:
        command = command_entry.get()
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output_text.insert(tk.END, result.stdout)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Function to handle closing any open list
def close_open_lists(event):
    for child in root.winfo_children():
        if isinstance(child, tk.Frame):
            child.place_forget()

# Bind the function to close open lists to the left mouse click event on the root window
root.bind("<Button-1>", close_open_lists)

# Create a function to set up a custom combobox
def create_custom_combobox(row, column, options, default_value):
    # Create a combobox-like entry widget
    combobox_entry = ttk.Entry(root)
    combobox_entry.grid(row=row, column=column, padx=10, pady=10)

    # Create a Listbox to act as the dropdown list with a scrollbar
    listbox_frame = tk.Frame(root)
    listbox = tk.Listbox(listbox_frame, font=('TkDefaultFont', 12), width=20)
    scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=listbox.yview)
    listbox.config(yscrollcommand=scrollbar.set)

    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    for option in options:
        listbox.insert(tk.END, option)

    # Function to handle item selection
    def select_item(event):
        selection = listbox.curselection()
        if selection:  # Check if there is a selection
            selected_item = listbox.get(selection)
            combobox_entry.delete(0, tk.END)
            combobox_entry.insert(0, selected_item)
            combobox_entry.focus_set()  # Set focus to the entry
            listbox_frame.place_forget()  # Close the listbox

    # Bind the selection event to the Listbox
    listbox.bind("<Button-1>", select_item)

    # Function to show/hide the dropdown list
    def toggle_dropdown(event=None):
        close_open_lists(None)  # Close any open lists first
        if not listbox_frame.winfo_ismapped():
            listbox_frame.place(x=combobox_entry.winfo_x(), y=combobox_entry.winfo_y() + combobox_entry.winfo_height())
            listbox_frame.lift()

    # Function to filter options based on entry text
    def filter_options(event):
        typed = combobox_entry.get()
        listbox.delete(0, tk.END)
        for option in options:
            if typed.lower() in option.lower():
                listbox.insert(tk.END, option)
        if listbox.size() > 0:
            toggle_dropdown()

    # Bind the entry widget to the filter function
    combobox_entry.bind("<KeyRelease>", filter_options)

    # Bind the entry widget to toggle the dropdown list
    combobox_entry.bind("<Button-1>", toggle_dropdown)

    # Set the default value
    combobox_entry.insert(0, default_value)

    # Create a button to toggle the dropdown list
    dropdown_button = ttk.Button(root, text="▼", command=toggle_dropdown)
    dropdown_button.grid(row=row, column=column + 1, padx=(0, 10))





# Load and display the logo image
image = Image.open("/home/pi/Desktop/MECSware_GUI/logo.png")
image = image.convert("RGBA")  # Ensure the image has an alpha channel for transparency
image_resized = image.resize((180, 70), Image.ANTIALIAS)
logo = ImageTk.PhotoImage(image_resized)
logo_label = tk.Label(frame, image=logo, bg="ghost white")
logo_label.grid(row=1, column=6, rowspan=2, columnspan=2)  # Adjust the position as needed
#logo_label.place(x=600, y=300)  # Adjust the position as needed

width_c = 15

# Create labels and entry fields for Name, ID, and Band
name_label = ttk.Label(frame, text="Name:", width=width_c-5, anchor=tk.E)
name_label.grid(row=3, column=6)
name_entry = ttk.Entry(frame, width=width_c-5)
name_entry.insert(0, "BS-114")
name_entry.grid(row=3, column=7, sticky=tk.W)

id_label = ttk.Label(frame, text="ID:", width=width_c-5, anchor=tk.E)
id_label.grid(row=4, column=6)
id_entry = ttk.Entry(frame, width=width_c-5)
id_entry.insert(0, "14")
id_entry.grid(row=4, column=7, sticky=tk.W)

band_label = ttk.Label(frame, text="Band:", width=width_c-5, anchor=tk.E)
band_label.grid(row=5, column=6)
band_entry = ttk.Entry(frame, width=width_c-5)
band_entry.insert(0, "78")
band_entry.grid(row=5, column=7, sticky=tk.W)

# Create labels and entry fields for IP Address and Port
ip_label = ttk.Label(frame, text="IP Address:", width=width_c, anchor=tk.E)
ip_label.grid(row=0, column=0, columnspan=1)
ip_entry = ttk.Entry(frame, width=width_c, justify='center')
ip_entry.insert(0, "10.0.1.2")
ip_entry.grid(row=0, column=1, columnspan=1)

port_label = ttk.Label(frame, text="Port:", width=width_c, anchor=tk.E)
port_label.grid(row=0, column=2)
port_entry = ttk.Entry(frame, width=width_c, justify='center')
port_entry.insert(0, "6327")
port_entry.grid(row=0, column=3, columnspan=1)

# Create labels for current and desired settings
x_spacing = 10
y_spacing = 20

current_settings_label = ttk.Label(frame, text="Current Settings", width=width_c, anchor=tk.CENTER, font=bold_font)
current_settings_label.grid(row=1, column=1, columnspan=2, pady= y_spacing, padx=x_spacing)

desired_settings_label = ttk.Label(frame, text="Desired Settings", width=width_c, anchor=tk.CENTER, font=bold_font)
desired_settings_label.grid(row=1, column=3, columnspan=2, pady=y_spacing, padx=x_spacing)

freq_label = ttk.Label(frame, text="[MHz]", width=width_c-10, anchor=tk.W, font=Entries_bold_font)
freq_label.grid(row=2, column=5, pady=(5), sticky=tk.W)

bw_label = ttk.Label(frame, text="[MHz]", width=width_c-10, anchor=tk.W, font=Entries_bold_font)
bw_label.grid(row=3, column=5, pady=(10,0), sticky=tk.W)

ratio_label = ttk.Label(frame, text="Ratio:", width=width_c, anchor=tk.E, font=Entries_bold_font)
ratio_label.grid(row=4, column=0)

power_label = ttk.Label(frame, text="[dBm]", width=width_c-10, anchor=tk.W, font=Entries_bold_font)
power_label.grid(row=5, column=5, pady=(10,0), sticky=tk.W)

# Create custom comboboxes for frequency, bandwidth, ratio, and power
create_custom_combobox(row=2, column=3, options=freq_options, default_value="3700")
create_custom_combobox(row=3, column=3, options=bw_options, default_value="20")
create_custom_combobox(row=4, column=3, options=ratio_options, default_value="5:5")
create_custom_combobox(row=5, column=3, options=power_options, default_value="20")

# Create labels to display the current settings
current_freq_label = ttk.Label(frame, text="Frequency:", width=width_c, anchor=tk.E, font=Entries_bold_font)
current_freq_label.grid(row=2, column=0, pady=(5))
frequency_label = ttk.Label(frame, text="", width=width_c, anchor=tk.W, justify='center')
frequency_label.grid(row=2, column=1, pady=(5))

current_bw_label = ttk.Label(frame, text="Bandwidth:", width=width_c, anchor=tk.E, font=Entries_bold_font)
current_bw_label.grid(row=3, column=0, pady=5)
bandwidth_label = ttk.Label(frame, text="", width=width_c, anchor=tk.W, justify='center')
bandwidth_label.grid(row=3, column=1, pady=5)

current_power_label = ttk.Label(frame, text="Power:", width=width_c, anchor=tk.E, font=Entries_bold_font)
current_power_label.grid(row=5, column=0, pady=5)
power_label = ttk.Label(frame, text="", width=width_c, anchor=tk.W, justify='center')
power_label.grid(row=5, column=1, pady=5)

# Create a button to test the connection
test_button = ttk.Button(frame, text="Test Connection", command=ping_command)
test_button.grid(row=0, column=5, pady=5, columnspan=2, sticky=tk.W)

# Create a button to get current data
get_data_button = ttk.Button(frame, text="Get Current Data", command=get_current_data)
get_data_button.grid(row=6, column=1, pady=(25,15), columnspan=2)

# Create a button to submit the command
submit_button = ttk.Button(frame, text="Submit Command", command=submit_command)
submit_button.grid(row=6, column=3, pady=(25, 15), columnspan=2)

# Configure row and column weights to allow resizing
frame.grid_rowconfigure(7, weight=1)  # Row containing the output_text widget
frame.grid_columnconfigure(0, weight=1)  # Allow horizontal expansion for the output_text widget

# Create a text widget to display the output
output_text = tk.Text(frame, bg="black", fg="white")
output_text.grid(row=7, column=0, columnspan=8, pady=(15,0), padx=(30,20), sticky="nsew")

# Start the main event loop
root.mainloop()