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
        # Create menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Create "File" menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Create New .HLPVA AI", command=self.create_hlpva)
        file_menu.add_command(label="Open .HLPVA AI", command=self.open_hlpva)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

    def create_hlpva(self):
        # Ask for the AI name
        ai_name = simpledialog.askstring("AI Name", "Enter a name for your AI:")
        if ai_name:
            # Ask user for file location to save the AI
            file_name = filedialog.asksaveasfilename(defaultextension=".HLPVA", filetypes=[("HLPVA files", "*.HLPVA")])
            if file_name:
                # Create a SimpleChatBot instance with the given name
                chatbot = SimpleChatBot(ai_name)

                # Open editor window to get the training pairs
                self.open_editor(chatbot, file_name)

    def open_editor(self, chatbot, file_name):
        # Create a new window for entering training pairs
        editor_window = tk.Toplevel(self.root)
        editor_window.title(f"Edit Training Pairs - {chatbot.name}")
        editor_window.geometry("600x400")

        # Create text box for entering training pairs
        self.editor_text = tk.Text(editor_window, height=20, width=50)
        self.editor_text.pack(padx=10, pady=10)

        # Populate the editor with current training data (if any)
        for user_input, bot_response in chatbot.training_data.items():
            self.editor_text.insert(tk.END, f"{user_input}: {bot_response}\n")

        # Create a frame for buttons (Run and Pre-train)
        button_frame = tk.Frame(editor_window)
        button_frame.pack(pady=10)

        # Create Run button to save and run the chatbot
        run_button = tk.Button(button_frame, text="Run", command=lambda: self.save_and_run(chatbot, file_name))
        run_button.pack(side=tk.LEFT, padx=5)

        # Create Pre-train button
        pretrain_button = tk.Button(button_frame, text="Pre-train", command=lambda: self.pre_train(chatbot))
        pretrain_button.pack(side=tk.LEFT, padx=5)

    def pre_train(self, chatbot):
        # Ask for the AI name again to personalize the pre-training
        ai_name = simpledialog.askstring("AI Name", "Enter the AI name for pre-training:")
        if ai_name:
            # Predefined questions and answers for the AI
            predefined_pairs = [
                (f"What is your name?", f"My name is {ai_name}."),
                (f"Who are you?", f"I am {ai_name}, your virtual assistant."),
                (f"Can you help me?", f"Yes, I can help you with anything, just ask me."),
                (f"What can you do?", f"I can answer your questions and assist you."),
                (f"How are you?", f"I am just a program, but I'm doing well, thank you."),
                (f"Hello", f"Hello i am {ai_name} i can Help You Just Code Me To!"),
                (f"Bye", f"Awww Bye But please Stay *w*"),
                (f"Is your Name {ai_name}", "Yes it is *w*"),
                (f"Fuck you", f"Thats not Very Nice...."),
                (f"Sorry", f"its okay!"),
                (f"Im sad", f"Its okay Heres a joke'What do you call a green egg its Shreck!!' Haha"),
                (f"What time is it?", f"i Dont know?"),
                (f"Whats the weather?", f"uhh... look at the forcats?"),
                (f"Whats the date?", f"idk check?"),
                (f"im bored!", f"play a game!")
                
            ]

            # Add the predefined pairs to the chatbot's training data
            for user_input, bot_response in predefined_pairs:
                chatbot.add_training_pair(user_input, bot_response)

            # Populate the editor window with the predefined pairs
            self.editor_text.delete("1.0", tk.END)  # Clear current content
            for user_input, bot_response in chatbot.training_data.items():
                self.editor_text.insert(tk.END, f"{user_input}: {bot_response}\n")

            # Notify the user
            messagebox.showinfo("Pre-training complete", f"{ai_name} has been pre-trained with basic responses!")

    def save_and_run(self, chatbot, file_name):
        # Get all lines from the editor text box
        training_pairs = self.editor_text.get("1.0", tk.END).strip().split("\n")

        # Process each line and add it as a training pair
        for line in training_pairs:
            if ':' in line:
                user_input, bot_response = line.split(":", 1)
                chatbot.add_training_pair(user_input.strip(), bot_response.strip())

        # Save the chatbot model to the .HLPVA zip file
        with zipfile.ZipFile(file_name, 'w') as hlpva_zip:
            # Save the chatbot model in a pickle file
            with open('chatbot.pkl', 'wb') as model_file:
                pickle.dump(chatbot, model_file)

            # Add the model to the .HLPVA zip file
            hlpva_zip.write('chatbot.pkl', 'chatbot.pkl')
            os.remove('chatbot.pkl')  # Clean up the temporary file

        # Close the editor window and start the chat
        self.start_chat(chatbot)

    def open_hlpva(self):
        # Ask user to select a .HLPVA file
        file_name = filedialog.askopenfilename(filetypes=[("HLPVA files", "*.HLPVA")])
        if file_name:
            with zipfile.ZipFile(file_name, 'r') as hlpva_zip:
                # Extract chatbot model from the .HLPVA file
                hlpva_zip.extract('chatbot.pkl', 'temp/')
                with open('temp/chatbot.pkl', 'rb') as model_file:
                    chatbot = pickle.load(model_file)

                # Remove extracted model after use
                os.remove('temp/chatbot.pkl')

                # Open the training editor and let user modify
                self.open_editor(chatbot, file_name)

    def start_chat(self, chatbot):
        # Create a new window for the chat interface
        chat_window = tk.Toplevel(self.root)
        chat_window.title(f"Talk to {chatbot.name}")  # Use AI name in the window title
        chat_window.geometry("400x400")

        # Create chat history display
        self.chat_history = tk.Text(chat_window, state=tk.DISABLED, height=20, width=50)
        self.chat_history.pack(padx=10, pady=10)

        # User input field
        self.user_input = tk.Entry(chat_window, width=50)
        self.user_input.pack(padx=10, pady=10)
        self.user_input.bind("<Return>", lambda event: self.send_message(chatbot))

    def send_message(self, chatbot):
        user_message = self.user_input.get()
        if user_message.strip():
            # Display user message in the chat history
            self.chat_history.config(state=tk.NORMAL)
            self.chat_history.insert(tk.END, f"You: {user_message}\n")
            self.chat_history.config(state=tk.DISABLED)
            self.chat_history.yview(tk.END)

            # Get AI response based on the trained pairs
            ai_response = chatbot.get_response(user_message)
            self.chat_history.config(state=tk.NORMAL)
            self.chat_history.insert(tk.END, f"{chatbot.name}: {ai_response}\n")  # Display chatbot name
            self.chat_history.config(state=tk.DISABLED)
            self.chat_history.yview(tk.END)

        # Clear input field
        self.user_input.delete(0, tk.END)

class SimpleChatBot:
    def __init__(self, name):
        self.name = name
        self.training_data = {}

    def add_training_pair(self, user_input, bot_response):
        # Add input-output pair to the training data
        self.training_data[user_input.lower()] = bot_response

    def get_response(self, user_input):
        # Attempt to match user input with training data
        user_input = user_input.lower()
        return self.training_data.get(user_input, "Sorry, I don't understand that.")

if __name__ == "__main__":
    root = tk.Tk()
    app = HLPVAApp(root)
    root.mainloop()