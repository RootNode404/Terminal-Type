import curses
import random

def main_loop(terminal):

    text = "The Quick Brown fox Jumps over the Lazy Dog"

    terminal = curses.initscr()
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()

    SCREEN_H, SCREEN_W = terminal.getmaxyx()
    X_CENTER = SCREEN_H // 2
    Y_CENTER = (SCREEN_W // 2) - (len(text) // 2)

    # Set some color
    curses.init_pair(1, curses.COLOR_WHITE, -1)  # Untyped letters
    curses.init_pair(2, curses.COLOR_GREEN, -1) # Typed letters
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Cursor

    # Print starting text
    terminal.addstr(X_CENTER, Y_CENTER, text, curses.color_pair(1))

    # Loop to handel typing
    current_index = 0
    key_shifted_pressed = "="
    while current_index < len(text):
        
        # Get the key pressed
        key_pressed = terminal.getch()

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
            terminal.addstr(X_CENTER, Y_CENTER, typed_chars, curses.color_pair(2))

            # Only show cursor if there is a new character to go to
            if current_cursor_char:
                terminal.addstr(X_CENTER, Y_CENTER + len(typed_chars), current_cursor_char, curses.color_pair(3))
            
            # Untyped characters
            terminal.addstr(X_CENTER, Y_CENTER + len(typed_chars) + 1, not_typed_chars, curses.color_pair(1))
            
            # Finally push it all to the display
            terminal.refresh()


# Encase main loop in a wrapper to catch error and handle exiting properly
curses.wrapper(main_loop)