#!/bin/python3
import curses, sys, os, json

class Editor():
    def __init__(self):
        self.screen = curses.initscr()
        self.screen.keypad(True)
        self.screen.nodelay(1)
        self.ROWS, self.COLS = self.screen.getmaxyx()
        self.ROWS -= 1
        curses.raw()
        curses.noecho()
        curses.mousemask(curses.ALL_MOUSE_EVENTS)  # Enable mouse events

    def reset(self):
        self.curx = 0
        self.cury = 0
        self.a_start = ''
        self.a_end = ''
        self.offx = 0
        self.offy = 0
        self.buff = []
        self.buffc = []
        self.total_lines = 0
        self.filename = 'Untitled.txt'
        self.annotations_start = []
        self.annotations_end = []
        self.annotations_content = []
        self.ROWS,_ = self.screen.getmaxyx()
        self.ROWS -= 1+len(self.annotations_start)

    def move_cursor(self, key):
        row = self.buff[self.cury] if self.cury < self.total_lines else None
        if key == curses.KEY_LEFT:
            if self.curx != 0: self.curx -= 1
            elif self.cury > 0:
                self.cury -= 1
                self.curx = len(self.buff[self.cury])
        elif key == curses.KEY_RIGHT:
            if row is not None and self.curx < len(row):
                self.curx += 1
            elif row is not None and self.curx == len(row) and self.cury != self.total_lines-1:
                self.cury += 1
                self.curx = 0
        elif key == curses.KEY_UP:
            if self.cury != 0: self.cury -= 1
            else: self.curx = 0
        elif key == curses.KEY_DOWN:
            if self.cury < self.total_lines-1: self.cury += 1
            else: self.curx = len(self.buff[self.cury])
        row = self.buff[self.cury] if self.cury < self.total_lines else None
        rowlen = len(row) if row is not None else 0
        if self.curx > rowlen: self.curx = rowlen


    def jump_cursor(self,key):
        _, mx, my, _, _ = curses.getmouse()
        if 0 <= my < self.total_lines:
            self.cury = my
        if 0 <= mx <= len(self.buff[self.cury]):
            self.curx = mx
        else:
            self.curx = len(self.buff[self.cury])

    def skip_word(self, key):
        if key == 393:
            self.move_cursor(curses.KEY_LEFT)
            try:
                if self.buff[self.cury][self.curx] != ord(' '):
                    while self.buff[self.cury][self.curx] != ord(' '):
                        if self.curx == 0: break
                        self.move_cursor(curses.KEY_LEFT)
                elif self.buff[self.cury][self.curx] == ord(' '):
                    while self.buff[self.cury][self.curx] == ord(' '):
                        if self.curx == 0: break
                        self.move_cursor(curses.KEY_LEFT)
            except: pass
        if key == 402:
            self.move_cursor(curses.KEY_RIGHT)
            try:
                if self.buff[self.cury][self.curx] != ord(' '):
                    while self.buff[self.cury][self.curx] != ord(' '):
                        self.move_cursor(curses.KEY_RIGHT)
                elif self.buff[self.cury][self.curx] == ord(' '):
                    while self.buff[self.cury][self.curx] == ord(' '):
                        self.move_cursor(curses.KEY_RIGHT)
            except: pass

    def scroll_page(self, key):
        count = 0
        while count != self.ROWS:
            if key == 336:
                self.move_cursor(curses.KEY_DOWN)
                if self.offy < self.total_lines - self.ROWS: self.offy += 1
            elif key == 337:
                self.move_cursor(curses.KEY_UP)
                if self.offy: self.offy -= 1
            count += 1

    def scroll_buffer(self):
        if self.cury < self.offy: self.offy = self.cury
        if self.cury >= self.offy + self.ROWS: self.offy = self.cury - self.ROWS+1
        if self.curx < self.offx: self.offx = self.curx
        if self.curx >= self.offx + self.COLS: self.offx = self.curx - self.COLS+1



    def print_buffer(self):
        print_buffer = '\x1b[?25l'
        print_buffer += '\x1b[H'
        
        for row in range(self.ROWS):
            buffrow = row + self.offy
            if buffrow == 0:
                line_start = 0
            else:
                line_start = sum(self.buffc[:buffrow])
            if buffrow < self.total_lines:
                line_end = line_start+self.buffc[buffrow]
                rowlen = len(self.buff[buffrow]) - self.offx
                if rowlen < 0: rowlen = 0
                if rowlen > self.COLS: rowlen = self.COLS

                temp = ''.join([chr(c) for c in self.buff[buffrow][self.offx: self.offx + rowlen]])
                positions = []
                colors = []
                if self.a_start != '' and self.a_start >= line_start and self.a_start <= line_end: positions.append(self.a_start-line_start) 
                if self.a_start != '' and self.a_start >= line_start and self.a_start <= line_end: colors.append('\033[101m')
                if self.a_end != '' and self.a_end >= line_start and self.a_end <= line_end: positions.append(self.a_end-line_start)
                if self.a_end != '' and self.a_end >= line_start and self.a_end <= line_end: colors.append('\033[104m')
                

                starts, stops = consolidate_spans(self.annotations_start,self.annotations_end)
                span_starts = []
                for s in starts:
                    if s >= line_start and s <= line_end:
                        span_starts.append(s-line_start)
                span_ends = []
                for s in stops:
                    if s >= line_start and s <= line_end+1:
                        span_ends.append(s-line_start)

                temp = color_chars(temp,positions,colors,span_starts,span_ends)

                print_buffer += temp

            print_buffer += '\x1b[K'
            print_buffer += '\r\n'
        return print_buffer
    
    def print_footer(self):
        status = '\x1b[7m'
        annotation_list = ''
        if len(self.annotations_content) > 0:
            for start,stop,content in zip(self.annotations_start,self.annotations_end,self.annotations_content):
                    annotation_item = str(start)+ ',' + str(stop)+' '+content
                    while len(annotation_item) < self.COLS: annotation_item += ' '
                    annotation_list+=annotation_item
        status += annotation_list
        status_bar = self.filename + ' - ' + str(self.total_lines) + ' lines'
        pos = 'Annotation: Start ' + str(self.a_start) + ', End ' + str(self.a_end)
        while len(status_bar) < self.COLS - len(pos)-1: status_bar += ' '
        status += status_bar
        status += pos + ' '
        status += '\x1b[m'
        status += '\x1b[' + str(self.cury - self.offy+1) + ';' + str(self.curx - self.offx+1) + 'H'
        status += '\x1b[?25h'
        return status

    def update_screen(self):
        self.scroll_buffer()
        print_buffer = self.print_buffer()
        status_bar = self.print_footer()
        sys.stdout.write(print_buffer + status_bar)
        sys.stdout.flush()

    def resize_window(self):
        self.ROWS, self.COLS = self.screen.getmaxyx()
        self.ROWS -= 1+len(self.annotations_start)
        self.screen.refresh()
        self.update_screen()

    def read_keyboard(self):
        def ctrl(c): return ((c) & 0x1f)
        c = -1
        while (c == -1): c = self.screen.getch()
        if c == ctrl(ord('q')): self.exit()
        elif c == 65: self.annotate()
        elif c == curses.KEY_RESIZE: self.resize_window()
        elif c == curses.KEY_HOME: self.curx = 0
        elif c == curses.KEY_END: self.curx = len(self.buff[self.cury])
        elif c == curses.KEY_LEFT: self.move_cursor(c)
        elif c == curses.KEY_RIGHT: self.move_cursor(c)
        elif c == curses.KEY_UP: self.move_cursor(c)
        elif c == curses.KEY_DOWN: self.move_cursor(c)
        elif c == curses.KEY_MOUSE: self.jump_cursor(c)
        elif c == curses.KEY_BACKSPACE: self.delete_char()
        elif c == 337: self.scroll_page(337)
        elif c == 336: self.scroll_page(336)
        elif c == 402: self.skip_word(402)
        elif c == 393: self.skip_word(393)
        elif c == 115: self.set_start()
        elif c == 101: self.set_end()
        elif c == 83: self.save_to_json()
        elif c == 82: self.remove()

    def clear_prompt(self, line):
        command_line = '\x1b[' + str(self.ROWS+1+len(self.annotations_start)) + ';' + '0' + 'H'
        command_line += '\x1b[7m' + line
        pos = 'Annotation: Start ' + str(self.a_start) + ', End ' + str(self.a_end)
        while len(command_line) < self.COLS - len(pos) + 10: command_line += ' '
        command_line += pos + ' '
        command_line += '\x1b[' + str(self.ROWS+1+len(self.annotations_start)) + ';' + str(len(line)+1) + 'H'
        sys.stdout.write(command_line)
        sys.stdout.flush()

    def command_prompt(self, line):
        self.clear_prompt(line)
        self.screen.refresh()
        word = ''; c = -1; pos = 0
        while c != 0x1b:
            c = -1
            while (c == -1): c = self.screen.getch()
            if c == 10: break
            if c == curses.KEY_BACKSPACE or c == 127:
                pos -= 1
                if pos < 0: pos = 0; continue
                sys.stdout.write('\b')
                sys.stdout.write(' ')
                sys.stdout.write('\b')
                sys.stdout.flush()
                word = word[:len(word)-1]
            if c != curses.KEY_BACKSPACE and c != 127:
                pos += 1
                sys.stdout.write(chr(c))
                sys.stdout.flush()
                word += chr(c)
        self.update_screen()
        self.screen.refresh()
        return word

    def annotate(self):
        annotation = self.command_prompt('annotation: ')
        self.annotations_start.append(self.a_start)
        self.annotations_end.append(self.a_end+1)
        self.annotations_content.append(annotation)
        self.a_start = ''
        self.a_end = ''
        self.ROWS,_ = self.screen.getmaxyx()
        self.ROWS -= 1+len(self.annotations_start)

    def set_start(self):
        self.a_start = sum(self.buffc[:self.cury])+self.curx
        
    def set_end(self):
        self.a_end = sum(self.buffc[:self.cury])+self.curx

    def remove(self):
        id = self.command_prompt('remove (0-index): ')
        try: 
            id = int(id)
            if id < len(self.annotations_content) and id >=0:
                del self.annotations_content[id]
                del self.annotations_start[id]
                del self.annotations_end[id]
                self.ROWS,_ = self.screen.getmaxyx()
                self.ROWS -= 1+len(self.annotations_start)
                self.update_screen()
        except: 
            return

    def save_to_json(self):
        data = {
            "start": self.annotations_start,
            "end": self.annotations_end,
            "label": self.annotations_content
        }
        json_filename = os.path.splitext(self.filename)[0] + '.json'
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    def open_file(self, filename):
        self.reset()
        try:
            with open(filename) as f:
                content = f.read().split('\n')
                for row in content:
                    line = self.split_lines(row)
                    for s in line:
                        self.buff.append([ord(c) for c in s])
                        self.buffc.append(len(s))
                    self.buffc[-1] +=1
                    
        except: 
            self.buff.append([])
            self.buffc.append(0)
        if filename:
            self.filename = filename
            if '.txt' in filename: self.highlight = False
            else: self.highlight = True
        self.total_lines = len(self.buff)

        json_filename = os.path.splitext(self.filename)[0] + '.json'
        if os.path.exists(json_filename):
            with open(json_filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.annotations_start = data.get("start", [])
                self.annotations_end = data.get("end", [])
                self.annotations_content = data.get("label", [])

        self.ROWS -= 1+len(self.annotations_start)
        self.update_screen()

    def split_lines(self,s):
        if s == '':
            return ['']
        else:
            return [s[i:i+self.COLS] for i in range(0, len(s), self.COLS)]


    def exit(self):
        curses.endwin()
        sys.exit(0)

    def start(self):
        self.update_screen()
        while(True):
            self.read_keyboard()
            self.update_screen()

def color_chars(s, positions, color_code=['\033[101m','\033[104m'],span_starts=[],span_ends=[]):

    reset_code = '\033[49m'
    result = []
    
    color_i = 0
    for i, c in enumerate(s):
        if i in span_starts:
            result.append('\033[32m')
        if i in span_ends:
            result.append('\033[39m')
        if i in positions:
            result.append(color_code[color_i] + c + reset_code)
            color_i += 1
        else:
            result.append(c)
    if len(span_ends)>0 and span_ends[-1]>i:
        result.append('\033[39m')
    return ''.join(result)

def consolidate_spans(starts,stops):
    spans = sorted(zip(starts, stops))

    merged_starts = []
    merged_stops = []
    current_start, current_stop = None, None

    for start, stop in spans:
        if current_start is None:  # First span
            current_start, current_stop = start, stop
        elif start <= current_stop:  # Overlapping or nested span
            current_stop = max(current_stop, stop)  # Extend outermost span
        else:  # Non-overlapping span
            merged_starts.append(current_start)
            merged_stops.append(current_stop)
            current_start, current_stop = start, stop

    if current_start is not None:  # Add the last span
        merged_starts.append(current_start)
        merged_stops.append(current_stop)

    return merged_starts, merged_stops
if __name__ == '__main__':
    def main(stdscr):
        editor = Editor()
        if len(sys.argv) >= 2: editor.open_file(sys.argv[1])
        else: editor.open_file('example.txt')
        editor.start()

    curses.wrapper(main)