||Hirosinkan council||
==========================





import tkinter as tk   
from tkinter import filedialog, messagebox, simpledialog
import os
import zipfile
import pickle

class HLPVAApp:
    def __init__(self, root):
        self.root = root
        self.root.title("HLPVA Virtual Assistant Manager")
        self.root.geometry("600x400")
        self.create_widgets()

    def create_widgets(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Create New .HLPVA AI", command=self.create_hlpva)
        file_menu.add_command(label="Open .HLPVA AI", command=self.open_hlpva)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Add Brightness Button for dark/light mode toggle
        self.brightness_button = tk.Button(self.root, text="Brightness", command=self.toggle_brightness)
        self.brightness_button.pack(pady=10)

        # Initialize to light mode
        self.is_dark_mode = False
        self.apply_brightness()

    def toggle_brightness(self):
        self.is_dark_mode = not self.is_dark_mode
        self.apply_brightness()

    def apply_brightness(self):
        if self.is_dark_mode:
            self.root.config(bg="black")
            self.brightness_button.config(bg="grey", fg="white")
        else:
            self.root.config(bg="white")
            self.brightness_button.config(bg="lightgrey", fg="black")

    def create_hlpva(self):
        ai_name = simpledialog.askstring("AI Name", "Enter a name for your AI:")
        if ai_name:
            file_name = filedialog.asksaveasfilename(defaultextension=".HLPVA", filetypes=[("HLPVA files", "*.HLPVA")])
            if file_name:
                chatbot = SimpleChatBot(ai_name)
                self.open_editor(chatbot, file_name)

    def open_editor(self, chatbot, file_name):
        editor_window = tk.Toplevel(self.root)
        editor_window.title(f"Edit Training Pairs - {chatbot.name}")
        editor_window.geometry("600x400")

        editor_frame = tk.Frame(editor_window)
        editor_frame.pack(padx=10, pady=10)

        editor_scrollbar = tk.Scrollbar(editor_frame)
        editor_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.editor_text = tk.Text(editor_frame, height=20, width=50, yscrollcommand=editor_scrollbar.set)
        self.editor_text.pack(side=tk.LEFT)
        editor_scrollbar.config(command=self.editor_text.yview)

        # Insert existing training pairs into the editor
        for user_input, bot_response in chatbot.training_data.items():
            self.editor_text.insert(tk.END, f"{user_input}: {bot_response}\n")

        button_frame = tk.Frame(editor_window)
        button_frame.pack(pady=10)

        run_button = tk.Button(button_frame, text="Run & Save", command=lambda: self.save_and_run(chatbot, file_name))
        run_button.pack(side=tk.LEFT, padx=5)

        # Add a button to manage libraries
        library_button = tk.Button(button_frame, text="Manage Libraries", command=lambda: self.manage_libraries(chatbot, self.editor_text))
        library_button.pack(side=tk.LEFT, padx=5)

    def save_and_run(self, chatbot, file_name):
        training_pairs = self.editor_text.get("1.0", tk.END).strip().split("\n")
        for line in training_pairs:
            if ':' in line:
                user_input, bot_response = line.split(":", 1)
                chatbot.add_training_pair(user_input.strip(), bot_response.strip())

        # Save chatbot with training data and libraries
        with zipfile.ZipFile(file_name, 'w') as hlpva_zip:
            with open('chatbot.pkl', 'wb') as model_file:
                pickle.dump(chatbot, model_file)
            hlpva_zip.write('chatbot.pkl', 'chatbot.pkl')
            os.remove('chatbot.pkl')

        self.start_chat(chatbot)

    def open_hlpva(self):
        file_name = filedialog.askopenfilename(filetypes=[("HLPVA files", "*.HLPVA")])
        if file_name:
            if not os.path.exists('temp'):
                os.makedirs('temp')
            with zipfile.ZipFile(file_name, 'r') as hlpva_zip:
                hlpva_zip.extract('chatbot.pkl', 'temp/')

                with open('temp/chatbot.pkl', 'rb') as model_file:
                    chatbot = pickle.load(model_file)
                os.remove('temp/chatbot.pkl')
                self.open_editor(chatbot, file_name)

    def start_chat(self, chatbot):
        chat_window = tk.Toplevel(self.root)
        chat_window.title(f"Talk to {chatbot.name}")
        chat_window.geometry("600x400")

        chat_frame = tk.Frame(chat_window)
        chat_frame.pack(padx=10, pady=10)

        chat_scrollbar = tk.Scrollbar(chat_frame)
        chat_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.chat_history = tk.Text(chat_frame, state=tk.DISABLED, height=20, width=50, yscrollcommand=chat_scrollbar.set)
        self.chat_history.pack(side=tk.LEFT)
        chat_scrollbar.config(command=self.chat_history.yview)

        self.user_input = tk.Entry(chat_window, width=50)
        self.user_input.pack(padx=10, pady=10)
        self.user_input.bind("<Return>", lambda event: self.send_message(chatbot))

        button_frame = tk.Frame(chat_window)
        button_frame.pack(pady=10)

        self.save_button = tk.Button(button_frame, text="Save Chat", command=self.save_chat)
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.load_button = tk.Button(button_frame, text="Load Chat", command=self.load_chat)
        self.load_button.pack(side=tk.LEFT, padx=5)

    def save_chat(self):
        # Save chat history to a .txt file
        chat_history = self.chat_history.get("1.0", tk.END)
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, "w") as f:
                f.write(chat_history)
            messagebox.showinfo("Success", "Chat saved successfully.")

    def load_chat(self):
        # Load chat history from a .txt file
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, "r") as f:
                loaded_chat = f.read()
            self.chat_history.config(state=tk.NORMAL)
            self.chat_history.insert(tk.END, loaded_chat)
            self.chat_history.config(state=tk.DISABLED)
            messagebox.showinfo("Success", "Chat loaded successfully.")

    def send_message(self, chatbot):
        user_message = self.user_input.get()
        if user_message.strip():
            self.chat_history.config(state=tk.NORMAL)
            self.chat_history.insert(tk.END, f"You: {user_message}\n")
            self.chat_history.config(state=tk.DISABLED)

            ai_response = chatbot.get_response(user_message)
            self.chat_history.config(state=tk.NORMAL)
            self.chat_history.insert(tk.END, f"{chatbot.name}: {ai_response}\n")
            self.chat_history.config(state=tk.DISABLED)

        self.user_input.delete(0, tk.END)

    def manage_libraries(self, chatbot, editor_text):
        # Open a window to manage libraries
        library_window = tk.Toplevel(self.root)
        library_window.title("Manage Libraries")
        library_window.geometry("400x400")

        library_frame = tk.Frame(library_window)
        library_frame.pack(padx=10, pady=10)

        button_frame = tk.Frame(library_window)
        button_frame.pack(pady=10)

        # Create buttons for each library
        for library in chatbot.libraries:
            library_button = tk.Button(button_frame, text=library["library_name"], command=lambda l=library: self.open_library(l, chatbot, editor_text))
            library_button.pack(side=tk.TOP, pady=2)

        # Create a button to make a new library
        make_library_button = tk.Button(button_frame, text="Make Library", command=lambda: self.create_library(chatbot))
        make_library_button.pack(side=tk.TOP, pady=10)

    def open_library(self, library, chatbot, editor_text):
        # Open the details of the library and display its trainer pairs
        library_details = f"Library: {library['library_name']}\n"
        library_details += f"Author: {library['author']}\nAI Name: {library['ai_name']}\n\nTrainer Pairs:\n"
        for pair in library['trainer_pairs']:
            library_details += f"{pair[0]}: {pair[1]}\n"

        editor_text.delete("1.0", tk.END)
        for pair in library['trainer_pairs']:
            editor_text.insert(tk.END, f"{pair[0]}: {pair[1]}\n")

        messagebox.showinfo(f"Library: {library['library_name']}", library_details)

    def create_library(self, chatbot):
        library_name = simpledialog.askstring("Library Name", "Enter the name of the library:")
        author_name = simpledialog.askstring("Author", "Enter the author's name:")
        trainer_pairs_input = simpledialog.askstring("Trainer Pairs", "Enter the trainer pairs in the format 'input: response', separated by commas:")

        if library_name and author_name and trainer_pairs_input:
            trainer_pairs = []
            try:
                for pair in trainer_pairs_input.split(","):
                    user_input, bot_response = pair.split(":", 1)
                    user_input = user_input.strip()
                    bot_response = bot_response.strip()
                    chatbot.add_training_pair(user_input, bot_response)
                    trainer_pairs.append((user_input, bot_response))

                chatbot.add_library(library_name, chatbot.name, author_name, trainer_pairs)
                messagebox.showinfo("Success", "Library created successfully!")
            except ValueError:
                messagebox.showerror("Error", "Incorrect format for trainer pairs. Ensure each pair is 'input: response'.")

class SimpleChatBot:
    def __init__(self, name):
        self.name = name
        self.training_data = {}
        self.libraries = []

    def add_training_pair(self, user_input, bot_response):
        self.training_data[user_input.lower()] = bot_response

    def add_library(self, library_name, ai_name, author_name, trainer_pairs):
        library = {
            "library_name": library_name,
            "ai_name": ai_name,
            "author": author_name,
            "trainer_pairs": trainer_pairs
        }
        self.libraries.append(library)

    def get_response(self, user_input):
        return self.training_data.get(user_input.lower(), "Sorry, I don't understand that.")

if __name__ == "__main__":
    root = tk.Tk()
    app = HLPVAApp(root)
    root.mainloop()
