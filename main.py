import curses

def main_loop(terminal):

    text = "the quick brown fox jumps over the lazy dog"

    terminal = curses.initscr()
    curses.curs_set(0)
    curses.noecho()
    curses.start_color()
    curses.use_default_colors()

    curses.init_pair(1, curses.COLOR_RED, -1)
    curses.init_pair(2, curses.COLOR_GREEN, -1)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

    # Print starting text
    terminal.addstr(0, 1, text, curses.color_pair(1))


    current_index = 0
    while current_index < len(text):

        key_pressed = terminal.getch()

        if key_pressed == ord(text[current_index]):

            # After keypressed current_index becomes typed
            current_index += 1

            typed_chars = text[:current_index]

            # If not finished show next char as curser
            if current_index < len(text):
                cursor_char = text[current_index]
                not_typed_chars = text[current_index + 1:]
            else:
                cursor_char = ""
                not_typed_chars = ""

            terminal.clear()

            terminal.addstr(0, 1, typed_chars, curses.color_pair(2))

            if cursor_char:
                terminal.addstr(0, 1 + len(typed_chars), cursor_char, curses.color_pair(3))

            terminal.addstr(0, 1 + len(typed_chars) + 1, not_typed_chars, curses.color_pair(1))

            terminal.refresh()


curses.wrapper(main_loop)