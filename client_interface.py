import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3
from datetime import datetime

# Placeholder function for face recognition and access granting
def recognize_and_grant_access():
    recognized_user = recognize_face()
    if recognized_user:
        user_type = recognized_user.get('type')
        if user_type == 'student':
            confirm_student_identity(recognized_user)
        elif user_type == 'staff':
            confirm_staff_identity(recognized_user)
        else:
            messagebox.showerror("Access Denied", "Only students and staff members are allowed to access.")
    else:
        messagebox.showerror("Access Denied", "User not recognized.")

# Placeholder function for face recognition (replace with actual logic)
def recognize_face():
    name = simpledialog.askstring("Input", "Enter your name:")
    email = simpledialog.askstring("Input", "Enter your email:")
    user_type = simpledialog.askstring("Input", "Enter your type (student/staff):")

    if not name or not email or not user_type:
        messagebox.showerror("Error", "All fields are required.")
        return None

    recognized_user = {'name': name, 'email': email, 'type': user_type}
    return recognized_user

# Function to check if the user exists in the database
def user_exists(user_id, user_type):
    with sqlite3.connect('smart_gate_management.db') as conn:
        cursor = conn.cursor()
        if user_type == 'student':
            cursor.execute("SELECT * FROM Student WHERE student_id = ?", (user_id,))
        elif user_type == 'staff':
            cursor.execute("SELECT * FROM Staff WHERE staff_id = ?", (user_id,))
        result = cursor.fetchone()
    return result is not None

# Function to check if the vehicle exists in the database
def vehicle_exists(license_plate):
    with sqlite3.connect('smart_gate_management.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Vehicle WHERE license_plate = ?", (license_plate,))
        result = cursor.fetchone()
    return result is not None

# Function to check if the accessory exists in the database
def accessory_exists(accessory_type):
    with sqlite3.connect('smart_gate_management.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Accessories WHERE type = ?", (accessory_type,))
        result = cursor.fetchone()
    return result is not None

# Logging access events
def log_access(user, action, accessories='', vehicle_id=None):
    with sqlite3.connect('smart_gate_management.db') as conn:
        cursor = conn.cursor()
        timestamp = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO Logs (timestamp, student_id, staff_id, user_name, email, action, gate_id, accessories, vehicle_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            timestamp, user.get('id') if user.get('type') == 'student' else None, user.get('id') if user.get('type') == 'staff' else None, 
            user.get('name'), user.get('email'), action, 1, accessories, vehicle_id
        ))
        conn.commit()

# Function to prompt for vehicle details
def prompt_vehicle_details(user_id, user_type):
    vehicle_details = {}
    vehicle_details['make'] = simpledialog.askstring("Vehicle Details", "Enter Vehicle Make:")
    if not vehicle_details['make']:
        messagebox.showerror("Error", "Vehicle make is required.")
        return None

    vehicle_details['model'] = simpledialog.askstring("Vehicle Details", "Enter Vehicle Model:")
    if not vehicle_details['model']:
        messagebox.showerror("Error", "Vehicle model is required.")
        return None

    vehicle_details['color'] = simpledialog.askstring("Vehicle Details", "Enter Vehicle Color:")
    if not vehicle_details['color']:
        messagebox.showerror("Error", "Vehicle color is required.")
        return None

    vehicle_details['license_plate'] = simpledialog.askstring("Vehicle Details", "Enter License Plate Number:")
    if not vehicle_details['license_plate']:
        messagebox.showerror("Error", "License plate number is required.")
        return None

    if vehicle_exists(vehicle_details['license_plate']):
        log_vehicle_details(user_id, vehicle_details['make'], vehicle_details['model'], vehicle_details['color'], vehicle_details['license_plate'], user_type)
        return vehicle_details
    else:
        messagebox.showerror("Error", "Vehicle not registered. Access denied.")
        return None

# Logging vehicle details
def log_vehicle_details(owner_id, make, model, color, license_plate, owner_type):
    with sqlite3.connect('smart_gate_management.db') as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Vehicles (owner_id, owner_type, make, model, color, license_plate)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (owner_id, owner_type, make, model, color, license_plate))
        conn.commit()

# Function to prompt for accessory details
def prompt_accessories_details(user_id, user_type):
    accessories_details = []
    while True:
        accessory = {}
        accessory['type'] = simpledialog.askstring("Accessory Details", "Enter Accessory Type (or leave blank to finish):")
        if not accessory['type']:
            break

        accessory['description'] = simpledialog.askstring("Accessory Details", "Enter Accessory Description:")
        if not accessory['description']:
            messagebox.showerror("Error", "Accessory description is required.")
            return None

        accessory['quantity'] = simpledialog.askinteger("Accessory Details", "Enter Quantity:")
        if accessory['quantity'] is None:
            messagebox.showerror("Error", "Accessory quantity is required.")
            return None

        if accessory_exists(accessory['type']):
            accessories_details.append(accessory)
        else:
            messagebox.showerror("Error", f"Accessory '{accessory['type']}' not found. Access denied.")
            return None

    log_accessories_details(user_id, user_type, accessories_details)
    return accessories_details

# Logging accessory details
def log_accessories_details(user_id, user_type, accessories):
    with sqlite3.connect('smart_gate_management.db') as conn:
        cursor = conn.cursor()
        for accessory in accessories:
            cursor.execute("""
                INSERT INTO Accessories (user_id, user_type, type, description, quantity)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, user_type, accessory['type'], accessory['description'], accessory['quantity']))
        conn.commit()

# Function to grant access to verified users
def grant_access(user, user_type):
    user_id = simpledialog.askstring("User ID", "Enter your ID:")
    if not user_exists(user_id, user_type):
        messagebox.showerror("Access Denied", f"{user_type.capitalize()} ID not found in the database. Access denied.")
        return
    
    user['id'] = user_id

    with sqlite3.connect('smart_gate_management.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT is_locked_down FROM Gate_Status WHERE gate_id = 1")
        is_locked_down = cursor.fetchone()[0]

    if is_locked_down:
        messagebox.showerror("Access Denied", "The gate is currently on lockdown. Access denied.")
    else:
        log_access(user, 'enter')

        has_vehicle = messagebox.askyesno("Vehicle", "Do you have a vehicle?")
        if has_vehicle:
            vehicle_details = prompt_vehicle_details(user_id, user_type)
            if not vehicle_details:
                return

        has_accessories = messagebox.askyesno("Accessories", "Do you have accessories?")
        if has_accessories:
            accessories_details = prompt_accessories_details(user_id, user_type)
            if not accessories_details:
                return

        messagebox.showinfo("Access Granted", f"Access Granted to {user['name']}. The gate is now open.")

# Function to confirm student identity
def confirm_student_identity(user):
    grant_access(user, 'student')

# Function to confirm staff identity
def confirm_staff_identity(user):
    grant_access(user, 'staff')

# Handling guest access
def access_as_guest():
    def submit_login():
        name = name_entry.get().strip()  # Remove any leading/trailing whitespace
        if not name:
            messagebox.showerror("Error", "Name cannot be empty.")
            return

        with sqlite3.connect('smart_gate_management.db') as conn:
            cursor = conn.cursor()
            # Ensure case-insensitive matching by using LOWER function
            cursor.execute("SELECT * FROM Guests WHERE LOWER(name) = LOWER(?)", (name.lower(),))
            result = cursor.fetchone()

        if result:
            guest_details = {
                'name': result[1],
                'contact': result[2],
                'id_number': result[3],
                'age': result[4],
                'office_visiting': result[5],
                'person_visiting': result[6]
            }

            if guest_details['age'] >= 18:
                id_number = simpledialog.askstring("ID Number", "Enter your ID Number:")
                if not id_number:
                    messagebox.showerror("Error", "ID Number is required for guests 18 and above.")
                    return
                if id_number != guest_details['id_number']:
                    messagebox.showerror("Error", "ID Number does not match. Access denied.")
                    return

            prompt_access(guest_details)
        else:
            messagebox.showerror("Error", "Guest not found. Please contact administration.")

    def prompt_access(guest_details):
        access_window = tk.Toplevel()
        access_window.title("Grant Access")
        tk.Label(access_window, text="Do you want to grant access?").pack()
        tk.Button(access_window, text="Yes", command=lambda: (grant_access(guest_details, 'guest'), access_window.destroy())).pack()
        tk.Button(access_window, text="No", command=access_window.destroy).pack()

    login_window = tk.Toplevel()
    login_window.title("Guest Login")

    tk.Label(login_window, text="Name:").pack()
    name_entry = tk.Entry(login_window)
    name_entry.pack()

    tk.Button(login_window, text="Login", command=submit_login).pack()

# Creating the main window
root = tk.Tk()
root.title("Smart Gate Management System")

tk.Label(root, text="Smart Gate Management System", font=("Helvetica", 16)).pack(pady=20)

tk.Button(root, text="Recognize and Grant Access", command=recognize_and_grant_access).pack(pady=10)
tk.Button(root, text="Access as Guest", command=access_as_guest).pack(pady=10)

root.mainloop()
