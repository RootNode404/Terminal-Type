import curses
import time

# Helper function to align text
def center(terminal, text):

    h, w = terminal.getmaxyx()
    x = h // 2
    y = (w // 2) - (len(text) // 2)

    return x, y

# Function to print results to terminal
def results(terminal, errors, start_time, end_time, text):

    # Calculate wdm
    characters = len(text)
    total_time = end_time - start_time
    msg = ""

    wpm = f"Words Per Minute -> {round((characters / 5) * (60 / total_time) - errors, 2)}"
    accuracy = ((characters - errors) / characters) * 100


    X_CENTER, Y_CENTER = center(terminal, wpm)

    # Clear the terminal and print results
    terminal.clear()
    terminal.addstr(X_CENTER - 6, Y_CENTER, wpm)

    # Message if the user gets -percentage
    if accuracy < 0:
        msg = " bruh you kinda suck"

    terminal.addstr(X_CENTER - 5, Y_CENTER, f"Accuracy -> {round(accuracy, 2)}%{msg}")
    X_CENTER, Y_CENTER = center(terminal, "Press ENTER to restart or Q to quit.")
    terminal.addstr(X_CENTER + 3, Y_CENTER, f"Press ENTER to restart or Q to quit.")

    terminal.refresh()
    
    key_pressed = terminal.getch()

    if key_pressed == curses.KEY_ENTER:
        return "restart"
    elif key_pressed == ord("q"):
        return "exit"

# Function to handle key presses
def handle_keypresses(state, key, text):

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

    # Clear screen to start off with
    terminal.clear()
    
    # Get all 3 different states of characters
    typed_chars = text[:state["index"]]
    cursor_char = text[state["index"]:state["index"] + 1]
    untyped_chars = text[state["index"] + 1:]

    # Return cords to align text to center of terminal
    x, y = center(terminal, text)
    
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

# Main-loop to handle all main-loopy stuff
def main_loop(terminal):

    # Master state index thingo
    state = {
        "index": 0,
        "errors": 0,
        "started": False,
        "start_time": None,
        "incorrect": False,
    }
    
    text = "The quick brown fox jumps over the lazy dog"

    terminal = curses.initscr() # Dosen't need to be here but need it for vscode function autocompleations
    curses.curs_set(0)
    

    # Set some color
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1) # Typed letters
    curses.init_pair(2, curses.COLOR_WHITE, -1) # Untyped letters
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Cursor
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_RED)  # Cursor incorrect

    # Print starting text
    X_CENTER, Y_CENTER = center(terminal, text)
    terminal.addstr(X_CENTER, Y_CENTER, text, curses.color_pair(2))

    # Loop to handel typing
    finished = False
    while finished == False:

        # Get pressed key
        pressed_key = terminal.getch()

        finished = handle_keypresses(state, pressed_key, text)
        draw_term(terminal, text, state)

    
    # After while loop exits stop the timer
    end_time = time.perf_counter()

    return results(terminal, state["errors"], state["start_time"], end_time, text)




# Encase main loop in a wrapper to catch error and handle exiting properly
# Encase it in a while loop
status = "restart"
while status == "restart": 
    
    status = curses.wrapper(main_loop)

    if status == "exit":
        break
    else:
        status = "restart"