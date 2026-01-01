import curses
import time

def str_index(string, index):

    return string[:index] + string[index].upper() + string[index + 1:]

def add_char(string, index, char):

    return string[:index] + char + string[index:]


# Colors class
class c:
    B = '\033[94m'  # Blue
    C = '\033[96m'  # Cyan
    G = '\033[92m'  # Green
    Y = '\033[93m'  # Yellow
    R = '\033[91m'  # Red
    E = '\033[0m'   # End color
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    HEADER = '\033[95m'

# Wrapper for whole app to catch errors and handle them without leaving the terminal in a unusable state
def main(terminal):


    # Setup terminal and hide terminal curser
 
    terminal = curses.initscr()
    curses.curs_set(0)

    # Clear the screen
    terminal.clear()

    text = "the quick brown fox jumped over the lazy dog"

    # Get terminal dimentions, then math to get center with text
    SCREEN_H, SCREEN_W = terminal.getmaxyx()
    X_CENTER = SCREEN_H // 2
    Y_CENTER = (SCREEN_W // 2) - (len(text) // 2)

    # Print words
    terminal.addstr(X_CENTER, Y_CENTER, text)

     
    index = 0
    for char in text:
               
        while True:

            # Get key input from user
            while True:
                key = terminal.getch()
                if key: break

            # Check if key pressed is the next one in the string
            if key == ord(char):
                
                text = str_index(text, index)
            
                terminal.addstr(X_CENTER, Y_CENTER, text)
                index += 1 
        
                # Refresh screen
                terminal.refresh()
                break
    

    # Wait for key before exiting
    terminal.getch()
    

    


curses.wrapper(main)