import curses        # TUI functionality
import time          # Timing and wpm calc
import configparser  # Loading and saving of config files
import os.path       # Check of config file exists
import random        # Random number for random word generator

# Class to save and load personal bests
class config_file:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config_filename = "config.ini"
        self.best_run = {}

    # Function to check if a config file is present
    def check_for_config(self):
        
        # Only create a config file if one is not present
        if os.path.isfile(self.config_filename) == False:

            self.config["Best Run"] = {
                "wpm": 0,
                "acc": 0,
                "err": 0
                }
            
            # Create a new config and open it
            with open(self.config_filename, "x") as configfile:
                self.config.write(configfile)

        # Else if config is present then just load it
        elif os.path.isfile(self.config_filename) == True:
            self.load()

    # Function to load best runs
    def load(self, do_return=False):

        # Load config file
        self.config.read(self.config_filename)

        # Return best scores as a dictonary
        self.best_run = self.config["Best Run"]

        if do_return == True:
            return self.config["Best Run"]

    # Function to save config file
    def check_n_save(self, possible_new_best_scores):

        # Check if new score > than best
        if possible_new_best_scores["wpm"] > float(self.best_run["wpm"]):

            # Set the new best run
            self.config["Best Run"] = {
            "wpm": possible_new_best_scores["wpm"],
            "acc": possible_new_best_scores["acc"],
            "err": possible_new_best_scores["err"]
            }

            # Write it to the file
            with open(self.config_filename, "w") as configfile:
                self.config.write(configfile)   

            # return true :)
            return True
            
# Random word generator
def random_words(number_of_words):

    with open("./wordlist.txt", "r") as file:

        total_lines = 0
        wordlist = []

        # Count how many lines there are and also append each word to the wordlist
        for line in file.readlines():
            total_lines += 1
            wordlist.append(line.strip("\n"))

        # For each word needed generate a random int between the total_lines -1 and 0
        random_words = ""
        for i in range(number_of_words):

            # Random int
            random_num = random.randint(0, total_lines - 1)

            # Only run once
            if i == 0:
                random_words += wordlist[random_num]
            
            # All the other times
            else:
                random_words += " " + wordlist[random_num]
            
        file.close()
        return random_words

            


# Helper to center text
def print_center_text(term, text, color=curses.COLOR_WHITE, offsetX=0, offsetY=0):

    # Get center of terminal
    h, w = term.getmaxyx()
    x = h // 2
    y = (w // 2) - (len(text) // 2)

    # Check of is list or just one string
    if isinstance(text, tuple) == True:

        x = h // 2
        y = (w // 2) - (len(text[0]) // 2)
        
        for sub_text in text:
            term.addstr((x + offsetX), (y + offsetY), sub_text, color)
            x += 1
    
    # Else if just one string
    else:   
        term.addstr((x + offsetX), (y + offsetY), text, color)

# Draw the terminal typing
def draw_term(term, master_text, master_values):

    # Get the center of the screen realtive to the whole text
    h, w = term.getmaxyx()
    x = h // 2
    y = (w // 2) - (master_values["len_of_text"] // 2)

    # Clear the timer area before printing it. It was buggin and I didnt know what to do.
    term.move(x - 2, 0)
    term.clrtoeol()

    # Draw status bar for live wpm and time
    term.addstr(x -2, y, f"{master_values['current_wpm']} | {round(master_values['time_elapsed'], 2)}")

    # For each character in master_text
    y_offset = 0
    for char_index in master_text:

        # Get character
        char = master_text[char_index]["char"]

        # Match statement to set color
        match master_text[char_index]["state"]:

            case "typed":
                term.addstr(x, (y + y_offset), char, curses.color_pair(2))

            case "cursor":
                term.addstr(x, (y + y_offset), char, curses.color_pair(3))

            case "untyped":
                term.addstr(x, (y + y_offset), char, curses.color_pair(1))

            case "error":
                term.addstr(x, (y + y_offset), char, curses.color_pair(4))


        term.refresh()

        # Offset increase for each character
        y_offset += 1

# Function to handle key presses
def handle_typing(master_values, key, master_text):

    # Check if cursor_index is bigger than text legnth
    if master_values["cursor_index"] > master_values["len_of_text"] - 1:
        master_text[master_values["cursor_index"]]["state"] = "typed"
        return True
    
    # Check if key is an alphabetical letter or an ANSI(backspace, esc, enter) escape sequence
    if 32 <= key <= 126:

        # Move cursor
        if master_values["cursor_index"] >= 0 and master_values["cursor_index"] < master_values["len_of_text"]:
            master_text[master_values["cursor_index"] + 1]["state"] = "cursor"

        # Convert key to string
        char = chr(key)

        # Only run once to start the timer
        if master_values["started"] == False:
            
            # Set to True to prevent running of this again
            master_values["started"] = True
            # Get current time
            master_values["start_time"] = time.perf_counter()
        
        # Get the expected char to be typed
        expected_char = master_text[master_values["cursor_index"]]["char"]

        # If the character pressed matches the one that the cursor is on then set state to typed and move along
        if char == expected_char:

            # Set the char state to typed
            master_text[master_values["cursor_index"]]["state"] = "typed"

            # Move the cursor along one
            master_values["cursor_index"] += 1

        # Else if char pressed does not equal the current char
        elif char != expected_char:

            # Increase errors
            master_values["errors"] += 1

            # Set state of current char to error
            master_text[master_values["cursor_index"]]["state"] = "error"

            # Move the cursor along one
            master_values["cursor_index"] += 1
    
    # Backspace
    elif key in (curses.KEY_BACKSPACE, 127, 8) and master_values["cursor_index"] > 0:

        # Change the cursor char to untyped
        master_text[master_values["cursor_index"]]["state"] = "untyped"

        # Move the cursor back one
        master_values["cursor_index"] -= 1
        
        # Change the state to untyped, ready to be retyped
        master_text[master_values["cursor_index"]]["state"] = "cursor"

    else:
        return False

# Function to print results to screen
def print_results(term, master_values, config):

    # Caluclate wdm
    errors = master_values["errors"]
    characters = master_values["len_of_text"]
    accuuracy = round(((characters - errors) / characters) * 100, 2)
    wpm = round(
        ((master_values["cursor_index"] - errors) / 5) * (60 / master_values["total_time"]), 
        2
    )


    # Check for best run, if so then print message
    possible_bests = {
        "wpm": wpm,
        "acc": accuuracy,
        "err": errors
    }
    if config.check_n_save(possible_bests) == True:
        print_center_text(term, "New Best!", offsetX=-10)

    # Load bests
    bests = config.load(do_return=True)

    # Print the results to the screen
    print_center_text(term, (f"Words Per Minute -> {wpm} | Best -> {bests["wpm"]}", f"Accuracy -> {accuuracy}% | Best -> {bests["acc"]}%", f"Errors -> {errors} | Best -> {bests["err"]}"), offsetX=+4)


    print_center_text(term, "Press ENTER to restart or Q to quit", offsetX= +9)
    
    while True:
        
        key = term.getch()

        # Enter presses then restarts
        if key == 10:
            return "restart"
        
        # q key exits
        elif key == ord("q"):
            return "exit"


# The main loop for loopy things
def main_loop(term):

    # Some stuff to hold important info
    master_text = {}
    master_values = {
        
        # Typing
        "cursor_index": 0,
        "len_of_text": 0,
        "started": False,
        "errors": 0,
        "current_wpm": 0,

        # Timing
        "start_time": 0,
        "time_elapsed": 0

    }

    # Set some terminal prefs
    term = curses.initscr()
    curses.curs_set(0)  # Hide cursor
    term.nodelay(True)

    # Setup config file and check if present
    config = config_file()
    config.check_for_config()
    
    # Set some color
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_WHITE, -1) # Untyped letters
    curses.init_pair(2, curses.COLOR_GREEN, -1) # Typed letters
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Cursor
    curses.init_pair(4, curses.COLOR_RED, -1) # Incorrect

    # Clear terminal
    term.clear()

    # Set text and add it to the master dictionary
    text = random_words(10)
    index = 0
    for char in text:

        # Add each char to the master dictonary, along with the index and state
        master_text[index] = {
            "char": char,
            "state": "untyped"
        }

        index += 1


    # Set the legnth of the text
    master_values["len_of_text"] = index - 1

    # Print starting text, no need to use master_text as text is all one color and state
    print_center_text(term, text)
    

    # Loop to handle typeing
    finished = False
    while finished != True:

        # Get pressed key
        key = term.getch()

        # Little thingo to quickly check if key pressed for smoother update of live wpm and timer
        if key != -1:
            # Call key presses function to handle key presses
            finished = handle_typing(master_values, key, master_text)

        if master_values["cursor_index"] > 0:
            # Calcualte time elapsed between last keypress and this one to get current wpm
            master_values["time_elapsed"] = time.perf_counter() - master_values["start_time"]

            # Calculate live wpm from elapsed time
            master_values["current_wpm"] = round(
                ((master_values["cursor_index"] - master_values["errors"]) / 5) * (60 / master_values["time_elapsed"]),
                2
            )


        # Draw the terminal
        draw_term(term, master_text, master_values)

    
    # Get the finishing time
    master_values["total_time"] = master_values["time_elapsed"]

    # Finally print the results
    return print_results(term, master_values, config)

# Call main loop inside a wrapper to handle errors and exiting, call it inside a loop so user can restart
while True:

    # When app exits get the code returned
    exit_code = curses.wrapper(main_loop)

    # Restart app
    if exit_code == "restart":
        continue

    # Exit app
    elif exit_code == "exit":
        break