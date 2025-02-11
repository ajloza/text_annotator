import curses

def main(stdscr):
    stdscr.addstr("Press any key (press 'q' to quit)\n")

    while True:
        key = stdscr.getch()
        if key == ord('q'):
            break
        stdscr.clear()
        stdscr.addstr(f"Key: {key}\n")
        if key in curses.__dict__.values():
            for name, val in curses.__dict__.items():
                if isinstance(val, int) and val == key:
                    stdscr.addstr(f"Matches: {name}\n")

curses.wrapper(main)