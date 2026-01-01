import curses
import time

def main_loop(terminal):

    # Helper function to align text
    def align_text(text):

        h, w = terminal.getmaxyx()
        x = h // 2
        y = (w // 2) - (len(text) // 2)

        return x, y

    # Function to print results to terminal
    def results(errors, start_time, end_time):

        # Calculate wdm
        words = len(text.split())
        characters = len(text)
        total_time = end_time - start_time

        wpm = f"Words Per Minute -> {round((characters / 5) * (60 / total_time), 2)}"
        accuracy = ((characters - errors) / characters) * 100


        X_CENTER, Y_CENTER = align_text(wpm)

        # Clear the terminal and print results
        terminal.clear()
        terminal.addstr(X_CENTER - 8, Y_CENTER, wpm)
        terminal.addstr(X_CENTER - 7, Y_CENTER, f"Accuracy -> {round(accuracy, 2)}%")
        X_CENTER, Y_CENTER = align_text("Press ENTER to restart or Q to quit.")
        terminal.addstr(X_CENTER + 3, Y_CENTER, f"Press ENTER to restart or Q to quit.")

        terminal.refresh()

        if terminal.getch() == curses.KEY_ENTER:
            curses.wrapper(main_loop)
        elif terminal.getch() == ord("q"):
            exit()

    text = "The quick brown fox jumps over the lazy dog"

    terminal = curses.initscr()
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    

    # Set some color
    curses.init_pair(1, curses.COLOR_GREEN, -1) # Typed letters
    curses.init_pair(2, curses.COLOR_WHITE, -1) # Untyped letters
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Cursor
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_RED)  # Cursor incorrect

    # Print starting text
    X_CENTER, Y_CENTER = align_text(text)
    terminal.addstr(X_CENTER, Y_CENTER, text, curses.color_pair(2))

    # Loop to handel typing
    current_index = 0
    key_shifted_pressed = "=" # fix me
    errors = 0
    while current_index < len(text):
        
        # Get the key pressed
        key_pressed = terminal.getch()
        
        # Start stopwatch
        if current_index == 0:
            start_time = time.perf_counter()

        # If the key is a shift key then wait for the next key press
        if key_pressed == curses.KEY_SBEG:
            key_shifted_pressed = terminal.getch()
            shift_pressed = True
    
        # If key = current char or if shifted cahracter and shift pressed is true
        if (key_pressed == ord(text[current_index])) or (str(ord(key_shifted_pressed)).upper() == ord(text[current_index]) and (shift_pressed == True )):

            # After keypressed current_index becomes typed
            current_index += 1
            
            # Get all the typed chars relative to the index
            typed_chars = text[:current_index]

            # Only move cursor along if there is a next character
            if current_index < len(text):
                current_cursor_char = text[current_index]
                not_typed_chars = text[current_index + 1:]
                terminal.clear()
            else:
                current_cursor_char = ""
                not_typed_chars = ""

            
            # Typed Letters
            terminal.addstr(X_CENTER, Y_CENTER, typed_chars, curses.color_pair(1))

            # Only show cursor if there is a new character to go to
            if current_cursor_char:
                terminal.addstr(X_CENTER, Y_CENTER + len(typed_chars), current_cursor_char, curses.color_pair(3))
            
            # Untyped characters
            terminal.addstr(X_CENTER, Y_CENTER + len(typed_chars) + 1, not_typed_chars, curses.color_pair(2))
            

        
        elif key_pressed != ord(text[current_index]):
            terminal.addstr(X_CENTER, Y_CENTER + len(typed_chars), current_cursor_char, curses.color_pair(4))
            errors += 1


        # Finally push it all to the display
        terminal.refresh()

    
    # After while loop exits stop the timer
    end_time = time.perf_counter()

    results(errors, start_time, end_time)




# Encase main loop in a wrapper to catch error and handle exiting properly
curses.wrapper(main_loop)