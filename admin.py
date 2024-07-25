import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3
from datetime import datetime

# Initialize the database with the required tables
def initialize_database():
    with sqlite3.connect('smart_gate_management.db') as conn:
        cursor = conn.cursor()

        # Create Gate_Status table
        cursor.execute('''CREATE TABLE IF NOT EXISTS Gate_Status (
                            gate_id INTEGER PRIMARY KEY,
                            gate_name TEXT NOT NULL,
                            status TEXT NOT NULL,
                            is_locked_down INTEGER DEFAULT 0
                        )''')

        # Create Logs table
        cursor.execute('''CREATE TABLE IF NOT EXISTS Logs (
                            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            timestamp TEXT NOT NULL,
                            student_id INTEGER,
                            staff_id INTEGER,
                            user_name TEXT NOT NULL,
                            email TEXT NOT NULL,
                            action TEXT NOT NULL,
                            gate_id INTEGER,
                            accessories TEXT,
                            vehicle_id INTEGER,
                            guest_id INTEGER,
                            FOREIGN KEY (student_id) REFERENCES Student(student_id),
                            FOREIGN KEY (staff_id) REFERENCES Staff(staff_id),
                            FOREIGN KEY (gate_id) REFERENCES Gate_Status(gate_id),
                            FOREIGN KEY (guest_id) REFERENCES Guests(guest_id)
                        )''')

        # Create Guests table
        cursor.execute('''CREATE TABLE IF NOT EXISTS Guests (
                            guest_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            contact TEXT,
                            id_number TEXT,
                            age INTEGER CHECK(age >= 0),
                            office_visiting TEXT,
                            person_visiting TEXT,
                            entrance_time TEXT NOT NULL
                        )''')

        # Create Student table
        cursor.execute('''CREATE TABLE IF NOT EXISTS Student (
                            student_id INTEGER PRIMARY KEY,
                            name TEXT NOT NULL,
                            email TEXT NOT NULL,
                            contact TEXT,
                            username TEXT UNIQUE NOT NULL,
                            password TEXT NOT NULL,
                            department_id INTEGER,
                            access_level INTEGER DEFAULT 1,
                            FOREIGN KEY (department_id) REFERENCES Department(department_id)
                        )''')

        # Create Staff table
        cursor.execute('''CREATE TABLE IF NOT EXISTS Staff (
                            staff_id INTEGER PRIMARY KEY,
                            name TEXT NOT NULL,
                            email TEXT NOT NULL,
                            username TEXT UNIQUE NOT NULL,
                            password TEXT NOT NULL,
                            department_id INTEGER,
                            access_level INTEGER DEFAULT 1,
                            FOREIGN KEY (department_id) REFERENCES Department(department_id)
                        )''')

        # Create Vehicle table
        cursor.execute('''CREATE TABLE IF NOT EXISTS Vehicle (
                            vehicle_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            make TEXT NOT NULL,
                            model TEXT NOT NULL,
                            color TEXT,
                            license_plate TEXT UNIQUE NOT NULL,
                            owner_id INTEGER,
                            owner_type TEXT CHECK(owner_type IN ('Student', 'Staff')),
                            FOREIGN KEY (owner_id) REFERENCES Student(student_id) ON DELETE CASCADE,
                            FOREIGN KEY (owner_id) REFERENCES Staff(staff_id) ON DELETE CASCADE
                        )''')

        # Create Accessories table
        cursor.execute('''CREATE TABLE IF NOT EXISTS Accessories (
                            accessory_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            type TEXT NOT NULL,
                            description TEXT,
                            quantity INTEGER NOT NULL CHECK(quantity >= 0),
                            department_id INTEGER,
                            FOREIGN KEY (department_id) REFERENCES Department(department_id)
                        )''')

        # Initialize Gate_Status with default value
        cursor.execute("INSERT OR IGNORE INTO Gate_Status (gate_id, gate_name, status, is_locked_down) VALUES (1, 'Main Gate', 'closed', 0)")

# Initialize the gate status in the database if it doesn't exist
def initialize_gate_status():
    with sqlite3.connect('smart_gate_management.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Gate_Status WHERE gate_id = 1")
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO Gate_Status (gate_id, gate_name, status, is_locked_down) VALUES (1, 'Main Gate', 'closed', 0)")
        conn.commit()

# Update the gate status in the database
def update_gate_status(is_locked_down):
    with sqlite3.connect('smart_gate_management.db') as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE Gate_Status SET is_locked_down = ?, status = ? WHERE gate_id = 1", (is_locked_down, 'locked' if is_locked_down else 'unlocked'))
        conn.commit()

# Get the current gate status from the database
def get_gate_status():
    with sqlite3.connect('smart_gate_management.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT is_locked_down FROM Gate_Status WHERE gate_id = 1")
        result = cursor.fetchone()
        return result[0] if result else None

# Lockdown the gate
def lockdown_gate():
    update_gate_status(True)
    messagebox.showinfo("Gate Status", "The gate has been locked down.")
    gate_status_var.set("Gate is on lockdown")

# Unlock the gate
def unlock_gate():
    update_gate_status(False)
    messagebox.showinfo("Gate Status", "The gate has been unlocked.")
    gate_status_var.set("Gate is unlocked")

# View access logs
def view_access_logs(user_type):
    with sqlite3.connect('smart_gate_management.db') as conn:
        cursor = conn.cursor()
        if user_type == "verified":
            cursor.execute("SELECT * FROM Logs WHERE guest_id IS NULL")
        else:
            cursor.execute("SELECT * FROM Guests WHERE guest_id IS NOT NULL")
        logs = cursor.fetchall()

    logs_window = tk.Toplevel()
    logs_window.title(f"{user_type.capitalize()} User Access Logs")
    text_area = tk.Text(logs_window, wrap='word')
    text_area.pack(expand=1, fill='both')

    for log in logs:
        text_area.insert(tk.END, f"{log}\n")

# Register user and their vehicles and accessories
def register_user():
    def submit_registration():
        user_type = user_type_var.get()
        name = name_entry.get()
        email = email_entry.get()
        contact = contact_entry.get()
        username = username_entry.get()
        user_id = None

        if user_type == 'student':
            student_id = id_entry.get()
            if not student_id or not name or not email or not contact or not username:
                messagebox.showerror("Error", "All fields are required.")
                return
            
            with sqlite3.connect('smart_gate_management.db') as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO Student (student_id, name, email, contact, username, password) VALUES (?, ?, ?, ?, ?, ?)",
                               (student_id, name, email, contact, username, 'default_password'))
                conn.commit()
                user_id = student_id
        
        elif user_type == 'staff':
            staff_id = id_entry.get()
            if not staff_id or not name or not email or not contact or not username:
                messagebox.showerror("Error", "All fields are required.")
                return
            
            with sqlite3.connect('smart_gate_management.db') as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO Staff (staff_id, name, email, contact, username, password) VALUES (?, ?, ?, ?, ?, ?)",
                               (staff_id, name, email, contact, username, 'default_password'))
                conn.commit()
                user_id = staff_id
        
        else:
            messagebox.showerror("Error", "Invalid user type.")
            return
        
        if messagebox.askyesno("Register Vehicle and Accessories", f"{user_type.capitalize()} registered successfully. Register vehicle and accessories?"):
            register_vehicles(user_id, user_type)
            register_accessories(user_id, user_type)

    def register_vehicles(user_id, user_type):
        while True:
            vehicle_details = {
                'make': simpledialog.askstring("Vehicle Details", "Enter Vehicle Make:"),
                'model': simpledialog.askstring("Vehicle Details", "Enter Vehicle Model:"),
                'color': simpledialog.askstring("Vehicle Details", "Enter Vehicle Color:"),
                'license_plate': simpledialog.askstring("Vehicle Details", "Enter License Plate Number:")
            }
            
            if not all(vehicle_details.values()):
                messagebox.showerror("Error", "All vehicle details are required.")
                return None

            with sqlite3.connect('smart_gate_management.db') as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO Vehicle (owner_id, owner_type, make, model, color, license_plate) VALUES (?, ?, ?, ?, ?, ?)",
                               (user_id, user_type, vehicle_details['make'], vehicle_details['model'], vehicle_details['color'], vehicle_details['license_plate']))
                conn.commit()

            if not simpledialog.askstring("Add Another Vehicle", "Do you want to add another vehicle? (yes/no):").lower().startswith('y'):
                break

    def register_accessories(user_id, user_type):
        while True:
            accessory_details = {
                'type': simpledialog.askstring("Accessory Details", "Enter Accessory Type:"),
                'description': simpledialog.askstring("Accessory Details", "Enter Accessory Description:"),
                'quantity': simpledialog.askinteger("Accessory Details", "Enter Accessory Quantity:", minvalue=0)
            }

            if not all(accessory_details.values()):
                messagebox.showerror("Error", "All accessory details are required.")
                return None

            with sqlite3.connect('smart_gate_management.db') as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO Accessories (department_id, type, description, quantity) VALUES (?, ?, ?, ?)",
                               (user_id, accessory_details['type'], accessory_details['description'], accessory_details['quantity']))
                conn.commit()

            if not simpledialog.askstring("Add Another Accessory", "Do you want to add another accessory? (yes/no):").lower().startswith('y'):
                break

    registration_window = tk.Toplevel()
    registration_window.title("Register User")
    registration_window.configure(bg='cyan')

    tk.Label(registration_window, text="Select User Type:", bg='cyan').grid(row=0, column=0, padx=10, pady=5, sticky='w')
    user_type_var = tk.StringVar(value='student')
    tk.Radiobutton(registration_window, text="Student", variable=user_type_var, value='student', bg='cyan').grid(row=1, column=0, padx=10, pady=5, sticky='w')
    tk.Radiobutton(registration_window, text="Staff", variable=user_type_var, value='staff', bg='cyan').grid(row=1, column=1, padx=10, pady=5, sticky='w')

    tk.Label(registration_window, text="Name:", bg='cyan').grid(row=2, column=0, padx=10, pady=5, sticky='w')
    name_entry = tk.Entry(registration_window)
    name_entry.grid(row=2, column=1, padx=10, pady=5, sticky='w')

    tk.Label(registration_window, text="Email:", bg='cyan').grid(row=3, column=0, padx=10, pady=5, sticky='w')
    email_entry = tk.Entry(registration_window)
    email_entry.grid(row=3, column=1, padx=10, pady=5, sticky='w')

    tk.Label(registration_window, text="Contact:", bg='cyan').grid(row=4, column=0, padx=10, pady=5, sticky='w')
    contact_entry = tk.Entry(registration_window)
    contact_entry.grid(row=4, column=1, padx=10, pady=5, sticky='w')

    tk.Label(registration_window, text="Username:", bg='cyan').grid(row=5, column=0, padx=10, pady=5, sticky='w')
    username_entry = tk.Entry(registration_window)
    username_entry.grid(row=5, column=1, padx=10, pady=5, sticky='w')

    tk.Label(registration_window, text="ID Number:", bg='cyan').grid(row=6, column=0, padx=10, pady=5, sticky='w')
    id_entry = tk.Entry(registration_window)
    id_entry.grid(row=6, column=1, padx=10, pady=5, sticky='w')

    tk.Button(registration_window, text="Register", command=submit_registration, bg='white').grid(row=7, column=0, columnspan=2, pady=10)

# Register guest
def register_guest():
    def submit_guest_registration():
        name = name_entry.get()
        contact = contact_entry.get()
        id_number = id_entry.get()
        age = int(age_entry.get())
        office_visiting = office_entry.get()
        person_visiting = person_entry.get()

        if not name or not office_visiting or not person_visiting:
            messagebox.showerror("Error", "Name, office visiting, and person visiting are required.")
            return
        
        if age >= 18:
            if not id_number or not contact:
                messagebox.showerror("Error", "ID number and contact are required for guests above 18.")
                return
        else:
            id_number = None
            contact = None

        with sqlite3.connect('smart_gate_management.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO Guests (name, contact, id_number, age, office_visiting, person_visiting, entrance_time)
                              VALUES (?, ?, ?, ?, ?, ?, ?)''',
                           (name, contact, id_number, age, office_visiting, person_visiting, datetime.now().isoformat()))
            conn.commit()

        messagebox.showinfo("Success", "Guest registered successfully.")
        guest_registration_window.destroy()

    guest_registration_window = tk.Toplevel()
    guest_registration_window.title("Register Guest")
    guest_registration_window.configure(bg='cyan')

    tk.Label(guest_registration_window, text="Name:", bg='cyan').grid(row=0, column=0, padx=10, pady=5, sticky='w')
    name_entry = tk.Entry(guest_registration_window)
    name_entry.grid(row=0, column=1, padx=10, pady=5, sticky='w')

    tk.Label(guest_registration_window, text="Contact:", bg='cyan').grid(row=1, column=0, padx=10, pady=5, sticky='w')
    contact_entry = tk.Entry(guest_registration_window)
    contact_entry.grid(row=1, column=1, padx=10, pady=5, sticky='w')

    tk.Label(guest_registration_window, text="ID Number:", bg='cyan').grid(row=2, column=0, padx=10, pady=5, sticky='w')
    id_entry = tk.Entry(guest_registration_window)
    id_entry.grid(row=2, column=1, padx=10, pady=5, sticky='w')

    tk.Label(guest_registration_window, text="Age:", bg='cyan').grid(row=3, column=0, padx=10, pady=5, sticky='w')
    age_entry = tk.Entry(guest_registration_window)
    age_entry.grid(row=3, column=1, padx=10, pady=5, sticky='w')

    tk.Label(guest_registration_window, text="Office Visiting:", bg='cyan').grid(row=4, column=0, padx=10, pady=5, sticky='w')
    office_entry = tk.Entry(guest_registration_window)
    office_entry.grid(row=4, column=1, padx=10, pady=5, sticky='w')

    tk.Label(guest_registration_window, text="Person Visiting:", bg='cyan').grid(row=5, column=0, padx=10, pady=5, sticky='w')
    person_entry = tk.Entry(guest_registration_window)
    person_entry.grid(row=5, column=1, padx=10, pady=5, sticky='w')

    tk.Button(guest_registration_window, text="Register", command=submit_guest_registration, bg='white').grid(row=6, column=0, columnspan=2, pady=10)

# Main application window
def main_app():
    global gate_status_var
    root = tk.Tk()
    root.title("Smart Gate Management System")
    root.configure(bg='cyan')

    gate_status_var = tk.StringVar()
    gate_status_var.set("Gate is on lockdown" if get_gate_status() else "Gate is unlocked")

    tk.Label(root, textvariable=gate_status_var, bg='cyan').pack(pady=10)

    button_frame = tk.Frame(root, bg='cyan')
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="Lockdown Gate", command=lockdown_gate, bg='white').grid(row=0, column=0, padx=10, pady=5)
    tk.Button(button_frame, text="Unlock Gate", command=unlock_gate, bg='white').grid(row=0, column=1, padx=10, pady=5)
    tk.Button(button_frame, text="View Verified User Access Logs", command=lambda: view_access_logs("verified"), bg='white').grid(row=1, column=0, padx=10, pady=5)
    tk.Button(button_frame, text="View Guest User Access Logs", command=lambda: view_access_logs("guest"), bg='white').grid(row=1, column=1, padx=10, pady=5)
    tk.Button(button_frame, text="Register User", command=register_user, bg='white').grid(row=2, column=0, padx=10, pady=5)
    tk.Button(button_frame, text="Register Guest", command=register_guest, bg='white').grid(row=2, column=1, padx=10, pady=5)

    root.mainloop()

# Initialize database and run the main application
initialize_database()
initialize_gate_status()
main_app()
