import tkinter as tk
from tkinter import messagebox, scrolledtext
from tkinter import ttk
import json
import subprocess
import psutil  # For getting CPU info
from PIL import Image, ImageTk  # Make sure Pillow is installed
import ttkbootstrap as ttkb  # Import TTK Bootstrap

# Global variable for the mining process
process = None

# Function to start XMRig
def start_mining():
    global process
    if process is not None:
        messagebox.showerror("Error", "Mining is already running!")
        return

    pool_url = pool_entry.get()
    wallet_address = wallet_entry.get()
    rig_id = rig_entry.get()

    if not pool_url or not wallet_address:
        messagebox.showerror("Error", "You need to enter a mining pool URL and Monero wallet address!")
        return

    # Create the config file
    config = {
        "autosave": True,
        "cpu": {
            "enabled": True,
            "priority": None,
            "max-threads-hint": 100,
            "huge-pages": True,
            "hw-aes": None,
            "asm": True
        },
        "pools": [
            {
                "url": pool_url,
                "user": wallet_address,
                "pass": "x",
                "rig-id": rig_id,
                "nicehash": False,
                "keepalive": True,
                "tls": False
            }
        ]
    }

    # Save the config file
    with open('config.json', 'w') as config_file:
        json.dump(config, config_file, indent=4)

    # Start XMRig with the config
    try:
        process = subprocess.Popen(['XMRIG/xmrig.exe', '-c', 'config.json'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        update_output()
        messagebox.showinfo("Mining", "Mining has started!")
    except FileNotFoundError:
        messagebox.showerror("Error", "XMRig not found. Make sure it's installed and added to PATH.")

# Function to update output from XMRig in real time
def update_output():
    if process is not None:
        output = process.stdout.readline()
        if output:
            console_output.insert(tk.END, output)
            console_output.see(tk.END)
        root.after(100, update_output)

# Function to stop mining
def stop_mining():
    global process
    if process is not None:
        process.terminate()
        process = None
        messagebox.showinfo("Mining", "Mining has been stopped.")
    else:
        messagebox.showwarning("Error", "Mining is not running.")

# Function to exit the app
def exit_app():
    if process is not None:
        stop_mining()
    if messagebox.askokcancel("Quit", "Do you really want to quit?"):
        root.quit()

# Function to update statistics
def update_statistics():
    if process is not None:
        cpu_usage = psutil.cpu_percent(interval=1)
        hashrate_label.config(text=f"Current Hashrate: {get_current_hashrate()} H/s")
        cpu_label.config(text=f"CPU Usage: {cpu_usage}%")
    root.after(2000, update_statistics)  # Update every 2 seconds

# Function to get the current hashrate from the console output
def get_current_hashrate():
    output_lines = console_output.get("1.0", tk.END).splitlines()
    for line in reversed(output_lines):
        if "H/s" in line:  # Check for hashrate line
            return line.split()[0]  # Return the first part of the line (hashrate)
    return "N/A"

# Creating the GUI app
root = tk.Tk()
root.title("XMR Forge")
root.geometry("600x600")
root.configure(bg="#1e1e1e")  # Dark background

# Load the logo for the window icon
icon_image = Image.open("monero_logo.png")
icon_image = icon_image.resize((32, 32), Image.LANCZOS)  # Resize to appropriate dimensions
icon = ImageTk.PhotoImage(icon_image)
root.iconphoto(True, icon)  # Set the window icon

# Add Monero logo and text
logo_frame = tk.Frame(root, bg="#1e1e1e")
logo_frame.pack(pady=(10, 10))

# Add logo
logo_image = Image.open("monero_logo.png")
logo_image = logo_image.resize((100, 100), Image.LANCZOS)
logo = ImageTk.PhotoImage(logo_image)
logo_label = tk.Label(logo_frame, image=logo, bg="#1e1e1e")
logo_label.pack(side=tk.LEFT)

# Add text next to the logo
text_label = tk.Label(logo_frame, text="XMR Forge", bg="#1e1e1e", fg="white", font=("Roboto", 16))
text_label.pack(side=tk.LEFT, padx=(10, 0))  # Space between logo and text

# Creating tabs
tab_control = ttk.Notebook(root)

# Tab for miner
miner_tab = ttk.Frame(tab_control)
tab_control.add(miner_tab, text='Miner')

# Label and entry for pool URL
tk.Label(miner_tab, text="Mining Pool URL:", bg="#1e1e1e", fg="white", font=("Arial", 12)).pack(pady=(20, 5))
pool_entry = tk.Entry(miner_tab, width=50, font=("Arial", 12))
pool_entry.pack(pady=5)

# Label and entry for wallet address
tk.Label(miner_tab, text="Monero Wallet Address:", bg="#1e1e1e", fg="white", font=("Arial", 12)).pack(pady=(20, 5))
wallet_entry = tk.Entry(miner_tab, width=50, font=("Arial", 12))
wallet_entry.pack(pady=5)

# Label and entry for Rig ID
tk.Label(miner_tab, text="Rig ID (optional):", bg="#1e1e1e", fg="white", font=("Arial", 12)).pack(pady=(20, 5))
rig_entry = tk.Entry(miner_tab, width=50, font=("Arial", 12))
rig_entry.pack(pady=5)

# Buttons for starting and stopping mining
start_button = ttkb.Button(miner_tab, text="Start Mining", command=start_mining, bootstyle="primary", width=20)
start_button.pack(pady=20)

# Stop mining button with orange color
stop_button = ttkb.Button(miner_tab, text="Stop Mining", command=stop_mining, bootstyle="danger", width=20)  # Changed to "danger"
stop_button.pack(pady=5)

# Console to display output from XMRig
tk.Label(miner_tab, text="Console:", bg="#1e1e1e", fg="white", font=("Arial", 12)).pack(pady=(20, 5))
console_output = scrolledtext.ScrolledText(miner_tab, width=70, height=15, bg="black", fg="white", insertbackground="green", font=("Courier", 10))
console_output.pack(pady=5)

# Exit button
exit_button = ttkb.Button(miner_tab, text="Exit", command=exit_app, bootstyle="secondary", width=20)
exit_button.pack(pady=(20, 5))

# Tab for statistics
statistics_tab = ttk.Frame(tab_control)
tab_control.add(statistics_tab, text='Statistics')

# Labels to display statistics
hashrate_label = tk.Label(statistics_tab, text="Current Hashrate: N/A H/s", bg="#1e1e1e", fg="white", font=("Arial", 12))
hashrate_label.pack(pady=(20, 5))

cpu_label = tk.Label(statistics_tab, text="CPU Usage: N/A%", bg="#1e1e1e", fg="white", font=("Arial", 12))
cpu_label.pack(pady=(20, 5))

# Start updating statistics
update_statistics()

# Tab for donations
donation_tab = ttk.Frame(tab_control)
tab_control.add(donation_tab, text='Donations')

# Label for the donation address
tk.Label(donation_tab, text="Donation Address:", bg="#1e1e1e", fg="white", font=("Arial", 12)).pack(pady=(20, 5))
donation_address = "463Vmgs2Uy3RqKQffG7VPpdzuec12DprXc5HiYz8kE1tKyp1Q3UNETYJ2Etu6S4Vmn7f3qQPeLoP5VLDWHxurG87VH3HJbN"  # XMR address
donation_entry = tk.Entry(donation_tab, width=50, font=("Arial", 12))
donation_entry.insert(0, donation_address)  # Set the default text
donation_entry.config(state='readonly')  # Make it read-only
donation_entry.pack(pady=5)

# Finalizing tab control
tab_control.pack(expand=1, fill='both')

# Start the GUI main loop
root.mainloop()