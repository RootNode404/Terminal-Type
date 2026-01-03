import curses
import time
import random
import configparser

# Class to save and load personal bests. used class becuase I was sick of functions
class config_file:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config_filename = "config.ini"

    # Load config file
    def load(self):

        # Load config file
        self.config.read(self.config_filename)

        # Load best wpm
        best_wpm = self.config["Personal Best"]["best_wpm"]

        return float(best_wpm)

    
    # Save lconfig file
    def save(self, new_best_wpm):

        # Compare new best wpm to saved one
        if new_best_wpm > self.load():

            self.config["Personal Best"] = {
                "best_wpm": new_best_wpm
            }

            # Write the config to the file
            with open(self.config_filename, "w") as configfile:
                self.config.write(configfile)

            return True
        
        return False

# Random word generator from wordlist.txt
def random_words(number_of_words):

    with open("./wordlist.txt", "r") as file:
        
        total_lines = 0
        wordlist = []
        
        # Count how many lines there are and also append them to the wordlist var
        for line in file.readlines():
            total_lines += 1
            wordlist.append(line.strip("\n"))
        
        # For each word neede generate a random int between the total_lines -1 and 0
        random_words = ""
        first_time = True
        for i in range(number_of_words):
            
            # Random int
            random_num = random.randint(0, total_lines -1)

            # Only run once
            if first_time == True:
                random_words += wordlist[random_num]
                first_time = False

            else:
                random_words += " " + wordlist[random_num]

        file.close()
        return random_words

# Helper function to center text
def center(terminal, text):

    h, w = terminal.getmaxyx()
    x = h // 2
    y = (w // 2) - (len(text) // 2)

    return x, y

# Function to print results to terminal
def results(terminal, state, end_time, text):

    # Calculate wdm
    characters = len(text)
    total_time = end_time - state["start_time"]
    accuracy = ((characters - state["errors"]) / characters) * 100
    wpm = state["current_wpm"]
    msg = ""

    # If wpm is bigger than personal best save it
    new_best = False
    cfg = config_file()
    if cfg.save(wpm) == True:
        new_best = True
        X_CENTER, Y_CENTER = center(terminal, "New Best!")
        terminal.addstr(X_CENTER - 5, Y_CENTER, f"New Best!")

    wpm = f"Words Per Minute -> {wpm} Best -> {cfg.load()}"
    X_CENTER, Y_CENTER = center(terminal, wpm)

    # Clear the terminal and print results
    terminal.addstr(X_CENTER + 5, Y_CENTER, wpm)

    # Message if the user gets -percentage
    if accuracy < 0:
        msg = " bruh you lowkey kinda suck"

    terminal.addstr(X_CENTER + 6, Y_CENTER, f"Accuracy -> {round(accuracy, 2)}%{msg}")
    terminal.addstr(X_CENTER + 7, Y_CENTER, f"Errors -> {state["errors"]}")
    X_CENTER, Y_CENTER = center(terminal, "Press ENTER to restart or Q to quit.")
    terminal.addstr(X_CENTER + 9, Y_CENTER, f"Press ENTER to restart or Q to quit.")

    terminal.refresh()

    # Probaly not the best way to handle exiting but thats a problem for future me, curses.KEY_ENTER stopped working for me so using 10 instead.
    match wait_for_key(terminal, (10, ord("q"))):
        case True:
            return "restart"
        case False:
            return "exit"

# Function to handle key presses
def handle_typing(state, key, text):

    # Check if index is bigger than the leg of text
    if state["index"] > len(text):
        return True  # Finished
    
    # Check if key is a alphabetical letter or an ANSI one
    if 32 <= key <= 126:
        char = chr(key)
    else:
        return False
    
    # Get the expected index char
    expected = text[state["index"]]

    if char == expected:
        if not state["started"]:
            state["started"] = True
            state["start_time"] = time.perf_counter()

        state["index"] += 1
        state["incorrect"] = False

    elif char != expected:
        state["errors"] += 1
        state["incorrect"] = True

    return state["index"] == len(text)

# Function to handle ui drawing 
def draw_term(terminal, text, state):
    
    # Get all 3 different states of characters
    typed_chars = text[:state["index"]]
    cursor_char = text[state["index"]:state["index"] + 1]
    untyped_chars = text[state["index"] + 1:]

    # Return cords to align text to center of terminal
    x, y = center(terminal, text)

    # Print status bar thing for live view of wpm
    terminal.addstr(x - 2, y, f"{state["current_wpm"]} | {round(state["elapsed"], 2)}")
    
    # Print typed characters
    terminal.addstr(x, y, typed_chars, curses.color_pair(1))

    # If cursor char present, print it to the terminal
    if cursor_char:

        if state["incorrect"] == True:
            terminal.addstr(x, y + len(typed_chars), cursor_char, curses.color_pair(4))

        elif state["incorrect"] == False:
            terminal.addstr(x, y + len(typed_chars), cursor_char, curses.color_pair(3))
    
    # Print untyped chars to terminal, only add 1 to y if cursor is present
    terminal.addstr(x, y + len(typed_chars) + (1 if cursor_char else 0), untyped_chars, curses.color_pair(2))

    # Finally refresh the screen
    terminal.refresh()

# Input helper function to wait for 2 certain key presses, e.g ENTER and Q
def wait_for_key(terminal, keys = ()):

    while True:

        key_pressed = terminal.getch()

        if key_pressed == keys[0]:
            return True
        elif key_pressed == keys[1]:
            return False
      
# Main-loop to handle all main-loopy stuff
def main_loop(terminal):

    # Master state index thingo
    state = {
        "index": 0,
        "errors": 0,
        "started": False,
        "start_time": None,
        "incorrect": False,
        "current_wpm": 0,
        "elapsed": 0,
    }

    terminal = curses.initscr() # Dosen't need to be here but need it for vscode function autocompleations
    curses.curs_set(0)
    terminal.nodelay(True)

    # Set some color
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1) # Typed letters
    curses.init_pair(2, curses.COLOR_WHITE, -1) # Untyped letters
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Cursor
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_RED)  # Cursor incorrect

    # Clear terminal
    terminal.clear()
    terminal.refresh()

    # Print starting text
    text = random_words(10)
    text = "the quick brown fox jumps over the lazy dog"
    X_CENTER, Y_CENTER = center(terminal, text)
    terminal.addstr(X_CENTER, Y_CENTER, text, curses.color_pair(2))

    # Loop to handel typing
    finished = False
    while finished == False:

        # Get pressed key
        key = terminal.getch()

        if key != -1:
            finished = handle_typing(state, key, text)

        # Calculate the eclypsed time between last key press and this one to get wpm
        if state["started"] == True:
            state["elapsed"] = time.perf_counter() - state["start_time"]
        else:
            state["elapsed"] = 0

        if state["elapsed"] > 0:
            state["current_wpm"] = round(
                ((state["index"] - state["errors"]) / 5) * (60 / state["elapsed"]),
                2
            )

        draw_term(terminal, text, state)

    
    # After while loop exits stop the timer
    end_time = time.perf_counter()

    return results(terminal, state, end_time, text)


# Encase main loop in a wrapper to catch error and handle exiting properly
# Encase it in a while loop
status = "restart"
while status == "restart": 
    
    status = curses.wrapper(main_loop)

    if status == "exit":
        break
    else:
        status = "restart"