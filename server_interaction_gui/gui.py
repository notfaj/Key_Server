import customtkinter as ctk
import requests
import base64


class KeyServerGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Key Server")
        self.geometry("700x500")

        # Username and password for basic authentication
        self.username = "admin"
        self.password = "12345"
        self.server = "http://localhost:5000"

        # Create tabs for different functionalities
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.pack(expand=True, fill="both")

        self.generate_tab = self.tab_view.add("Generate Key")
        self.info_tab = self.tab_view.add("Get Key Info")
        self.edit_tab = self.tab_view.add("Edit Key")
        self.logs_tab = self.tab_view.add("Request Logs")
        self.update_expiration_tab = self.tab_view.add("Update Expiration")
        self.delete_tab = self.tab_view.add("Delete Key")  # New tab for deleting keys

        # Setup each tab
        self.setup_generate_tab()
        self.setup_info_tab()
        self.setup_edit_tab()
        self.setup_logs_tab()
        self.setup_update_expiration_tab()
        self.setup_delete_tab()  # Setup for delete tab

    def setup_delete_tab(self):
        # Input for key to delete
        ctk.CTkLabel(self.delete_tab, text="Key to Delete:").pack(pady=(10, 0))
        self.key_delete_entry = ctk.CTkEntry(self.delete_tab)
        self.key_delete_entry.pack(pady=(0, 10))

        # Button to delete key
        ctk.CTkButton(self.delete_tab, text="Delete Key", command=self.delete_key).pack(
            pady=20
        )

        # Text box for console output
        self.console_delete = ctk.CTkTextbox(self.delete_tab, width=500, height=150)
        self.console_delete.pack(pady=(10, 20))

    def delete_key(self):
        key = self.key_delete_entry.get()

        url = f"{self.server}/delete-key?key={key}"
        auth = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
        headers = {"Authorization": f"Basic {auth}"}

        try:
            response = requests.delete(url, headers=headers)
            if response.status_code == 200:
                self.console_delete.insert("end", "Key Deleted Successfully\n")
            else:
                self.console_delete.insert(
                    "end", f"Error: {response.status_code} - {response.text}\n"
                )
        except Exception as e:
            self.console_delete.insert("end", f"Exception: {str(e)}\n")

    def setup_generate_tab(self):
        # Input fields for key generation parameters
        ctk.CTkLabel(self.generate_tab, text="Expiration Days:").pack(pady=(10, 0))
        self.expiration_entry = ctk.CTkEntry(self.generate_tab)
        self.expiration_entry.pack(pady=(0, 10))

        ctk.CTkLabel(self.generate_tab, text="Machine Limit:").pack(pady=(10, 0))
        self.machine_limit_entry = ctk.CTkEntry(self.generate_tab)
        self.machine_limit_entry.pack(pady=(0, 10))

        ctk.CTkLabel(self.generate_tab, text="Product Name:").pack(
            pady=(10, 0)
        )  # Updated label
        self.product_name_entry = ctk.CTkEntry(self.generate_tab)
        self.product_name_entry.pack(pady=(0, 10))

        # Button to generate key
        ctk.CTkButton(
            self.generate_tab, text="Generate Key", command=self.generate_key
        ).pack(pady=20)

        # Text box for console output
        self.console_generate = ctk.CTkTextbox(self.generate_tab, width=500, height=150)
        self.console_generate.pack(pady=(10, 20))

    def setup_info_tab(self):
        # Input for key to get information
        ctk.CTkLabel(self.info_tab, text="Key:").pack(pady=(10, 0))
        self.key_info_entry = ctk.CTkEntry(self.info_tab)
        self.key_info_entry.pack(pady=(0, 10))

        # Button to get key info
        ctk.CTkButton(
            self.info_tab, text="Get Key Info", command=self.get_key_info
        ).pack(pady=20)

        # Text box for console output
        self.console_info = ctk.CTkTextbox(self.info_tab, width=500, height=150)
        self.console_info.pack(pady=(10, 20))

    def setup_edit_tab(self):
        # Input fields for editing key info
        ctk.CTkLabel(self.edit_tab, text="Key:").pack(pady=(10, 0))
        self.key_edit_entry = ctk.CTkEntry(self.edit_tab)
        self.key_edit_entry.pack(pady=(0, 10))

        ctk.CTkLabel(self.edit_tab, text="New Expiration Days:").pack(pady=(10, 0))
        self.new_expiration_entry = ctk.CTkEntry(self.edit_tab)
        self.new_expiration_entry.pack(pady=(0, 10))

        ctk.CTkLabel(self.edit_tab, text="New Machine Limit:").pack(pady=(10, 0))
        self.new_machine_limit_entry = ctk.CTkEntry(self.edit_tab)
        self.new_machine_limit_entry.pack(pady=(0, 10))

        # Button to edit key
        ctk.CTkButton(self.edit_tab, text="Edit Key", command=self.edit_key).pack(
            pady=20
        )

        # Text box for console output
        self.console_edit = ctk.CTkTextbox(self.edit_tab, width=500, height=150)
        self.console_edit.pack(pady=(10, 20))

    def setup_logs_tab(self):
        # Button to request logs
        ctk.CTkButton(
            self.logs_tab, text="Get Request Logs", command=self.request_logs
        ).pack(pady=20)

        # Text box for console output
        self.console_logs = ctk.CTkTextbox(self.logs_tab, width=500, height=250)
        self.console_logs.pack(pady=(10, 20))

    def setup_update_expiration_tab(self):
        # Input fields for updating expiration
        ctk.CTkLabel(self.update_expiration_tab, text="Product ID:").pack(pady=(10, 0))
        self.update_product_id_entry = ctk.CTkEntry(self.update_expiration_tab)
        self.update_product_id_entry.pack(pady=(0, 10))

        ctk.CTkLabel(self.update_expiration_tab, text="Additional Days:").pack(
            pady=(10, 0)
        )
        self.additional_days_entry = ctk.CTkEntry(self.update_expiration_tab)
        self.additional_days_entry.pack(pady=(0, 10))

        # Button to update expiration
        ctk.CTkButton(
            self.update_expiration_tab,
            text="Update Expiration",
            command=self.update_expiration,
        ).pack(pady=20)

        # Text box for console output
        self.console_update = ctk.CTkTextbox(
            self.update_expiration_tab, width=500, height=150
        )
        self.console_update.pack(pady=(10, 20))

    def generate_key(self):
        expiration_days = self.expiration_entry.get()
        machine_limit = self.machine_limit_entry.get()
        product_name = self.product_name_entry.get()  # Get dynamic product name

        # Validation for input fields
        if (
            not expiration_days.isdigit()
            or not machine_limit.isdigit()
            or not product_name
        ):
            self.console_generate.insert(
                "end",
                "Please enter valid expiration days, machine limit, and product name.\n",
            )
            return

        url = f"{self.server}/generate-key?expiration_days={expiration_days}&machine_limit={machine_limit}&product_id={product_name}"
        auth = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
        headers = {"Authorization": f"Basic {auth}"}

        try:
            response = requests.post(url, headers=headers)
            print(url)
            if response.status_code == 201:
                key_info = response.json().get("key", "No key found")
                self.console_generate.insert("end", f"Key Generated: {key_info}\n")
            else:
                self.console_generate.insert(
                    "end", f"Error: {response.status_code} - {response.text}\n"
                )
        except Exception as e:
            self.console_generate.insert("end", f"Exception: {str(e)}\n")

    def get_key_info(self):
        key = self.key_info_entry.get()
        url = f"{self.server}/key-info?key={key}"
        auth = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
        headers = {"Authorization": f"Basic {auth}"}

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                key_info = response.json()
                # Prettify the key info output
                formatted_info = self.format_key_info(key_info)
                self.console_info.insert("end", f"{formatted_info}\n")
            else:
                self.console_info.insert(
                    "end", f"Error: {response.status_code} - {response.text}\n"
                )
        except Exception as e:
            self.console_info.insert("end", f"Exception: {str(e)}\n")

    def format_key_info(self, key_info):
        """Format the key info JSON for better readability."""
        if "key_info" not in key_info or "status" not in key_info:
            return "Invalid response format."

        key_data = key_info["key_info"]
        activated = "Yes" if key_data.get("activated", False) else "No"
        expiration_date = key_data.get("expiration_date", "N/A")
        expiration_days = key_data.get("expiration_days", "N/A")
        key = key_data.get("key", "N/A")
        machine_ids = key_data.get("machine_ids", [])
        machine_limit = key_data.get("machine_limit", "N/A")
        product_id = key_data.get("product_id", "N/A")

        # Construct a readable format
        formatted_output = (
            f"Key Info:\n"
            f"  Status: {key_info.get('status', 'Unknown')}\n"
            f"  Key: {key}\n"
            f"  Product ID: {product_id}\n"
            f"  Activated: {activated}\n"
            f"  Expiration Days: {expiration_days}\n"
            f"  Expiration Date: {expiration_date}\n"
            f"  Machine Limit: {machine_limit}\n"
            f"  Machine IDs: {', '.join(machine_ids) if machine_ids else 'None'}\n"
        )

        return formatted_output

    def edit_key(self):
        key = self.key_edit_entry.get()
        new_expiration_days = self.new_expiration_entry.get()
        new_machine_limit = self.new_machine_limit_entry.get()

        url = f"{self.server}/edit-key"
        auth = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
        headers = {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}
        data = {
            "key": key,
            "expiration_days": int(new_expiration_days),
            "machine_limit": int(new_machine_limit),
        }

        try:
            response = requests.put(url, headers=headers, json=data)
            if response.status_code == 200:
                self.console_edit.insert("end", "Key Updated Successfully\n")
            else:
                self.console_edit.insert(
                    "end", f"Error: {response.status_code} - {response.text}\n"
                )
        except Exception as e:
            self.console_edit.insert("end", f"Exception: {str(e)}\n")

    def request_logs(self):
        url = f"{self.server}/request-logs"
        auth = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
        headers = {"Authorization": f"Basic {auth}"}

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                logs = response.json()
                self.console_logs.insert("end", f"Request Logs: {logs}\n")
            else:
                self.console_logs.insert(
                    "end", f"Error: {response.status_code} - {response.text}\n"
                )
        except Exception as e:
            self.console_logs.insert("end", f"Exception: {str(e)}\n")

    def update_expiration(self):
        product_id = self.update_product_id_entry.get()
        additional_days = self.additional_days_entry.get()

        if not product_id or not additional_days.isdigit():
            self.console_update.insert(
                "end", "Please enter a valid product ID and number of days.\n"
            )
            return

        url = f"{self.server}/update-expiration"
        auth = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
        headers = {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}
        data = {"product_id": product_id, "additional_days": int(additional_days)}

        try:
            response = requests.put(url, headers=headers, json=data)
            if response.status_code == 200:
                self.console_update.insert(
                    "end",
                    f"Expiration updated successfully for product '{product_id}'.\n",
                )
            else:
                self.console_update.insert(
                    "end", f"Error: {response.status_code} - {response.text}\n"
                )
        except Exception as e:
            self.console_update.insert("end", f"Exception: {str(e)}\n")


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = KeyServerGUI()
    app.mainloop()
