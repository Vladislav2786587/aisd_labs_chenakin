import tkinter as tk

WALL = '0'
PATH = '1'
START = 'S'
EXIT = 'E'

maze = [
    ['0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0'],
    ['0','S','1','1','1','E','1','0','1','1','1','0','1','1','1','1','1','1','1','0'],
    ['0','1','0','0','0','0','1','0','1','0','1','0','1','0','0','0','0','0','1','0'],
    ['0','1','1','1','1','0','1','1','1','0','1','1','1','1','1','1','1','0','1','0'],
    ['0','0','0','0','1','0','0','0','1','0','0','0','0','0','0','0','1','0','1','0'],
    ['0','E','1','0','1','1','1','0','1','1','1','1','1','1','1','0','1','1','1','0'],
    ['0','1','0','0','0','0','1','0','0','0','0','0','0','0','1','0','0','0','1','0'],
    ['0','1','1','1','1','0','1','1','1','1','1','1','1','0','1','1','1','0','1','0'],
    ['0','0','0','0','1','0','0','0','1','0','0','0','1','0','0','0','1','0','1','0'],
    ['0','1','1','0','1','1','1','0','1','1','1','0','1','1','1','0','1','1','1','0'],
    ['0','1','0','0','0','0','1','0','1','0','E','0','1','0','0','0','1','0','0','0'],
    ['0','1','1','1','1','1','1','1','1','0','1','1','1','1','1','1','1','1','1','0'],
    ['0','1','0','0','0','0','0','0','1','0','0','0','0','0','0','0','0','0','1','0'],
    ['0','1','1','1','1','1','1','0','1','1','1','0','1','1','1','1','1','0','1','0'],
    ['0','1','0','0','0','0','1','0','0','0','1','0','1','0','0','0','1','0','1','0'],
    ['0','1','1','1','1','0','1','1','1','0','1','1','1','1','1','0','1','1','1','0'],
    ['0','1','0','0','1','0','0','0','1','0','0','0','1','0','0','0','1','0','0','0'],
    ['0','1','1','1','1','1','1','0','1','1','1','0','1','1','1','E','1','1','1','0'],
    ['0','1','0','0','0','0','1','0','1','0','1','0','1','0','0','0','0','0','E','0'],
    ['0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0'],
]

rows, cols = len(maze), len(maze[0])
cell_size = 28

root = tk.Tk()
root.title("Лабиринт. Ченакин В. ИСТбд-24")
root.configure(bg='#1a1a1a')

canvas = tk.Canvas(root, width=cols * cell_size, height=rows * cell_size, 
                   bg='#1a1a1a', highlightthickness=0)
canvas.pack(pady=10, padx=10)

info_frame = tk.Frame(root, bg='#1a1a1a')
info_frame.pack(pady=5)

info_label = tk.Label(info_frame, text="", font=('Arial', 12), 
                       bg='#1a1a1a', fg='white')
info_label.pack()

start_pos = None
visited = []
current_exits = 0

def get_color_and_style(i, j, cell_value):
    if start_pos and (i, j) == start_pos:
        return {
            'fill': '#4a90e2',
            'outline': '#2c6cb3',
            'width': 3,
            'text': 'старт',
            'text_color': 'white'
        }
    
    if cell_value == WALL:
        return {
            'fill': '#2d3436',
            'outline': '#636e72',
            'width': 1,
            'text': '',
            'text_color': 'white'
        }
    elif cell_value == EXIT:
        if (i, j) in visited:
            return {
                'fill': '#27ae60',
                'outline': '#2ecc71',
                'width': 3,
                'text': 'выход',
                'text_color': 'white'
            }
        else:
            return {
                'fill': '#c0392b',
                'outline': '#e74c3c',
                'width': 2,
                'text': 'выход',
                'text_color': 'white'
            }
    else:
        if (i, j) in visited:
            return {
                'fill': '#f39c12',
                'outline': '#e67e22',
                'width': 1,
                'text': '*',
                'text_color': 'white'
            }
        else:
            return {
                'fill': '#ecf0f1',
                'outline': '#bdc3c7',
                'width': 1,
                'text': '',
                'text_color': 'black'
            }

def draw_maze():

    canvas.delete("all")
    
    for i in range(rows):
        for j in range(cols):
            x1, y1 = j * cell_size, i * cell_size
            x2, y2 = x1 + cell_size, y1 + cell_size
            
            style = get_color_and_style(i, j, maze[i][j])
            canvas.create_rectangle(x1 + 2, y1 + 2, x2 - 2, y2 - 2,
                                   fill=style['fill'],
                                   outline=style['outline'],
                                   width=style['width'])
            if style['text']:
                canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2,
                                   text=style['text'],
                                   fill=style['text_color'],
                                   font=('Arial', 10, 'bold'))
def find_start():
    global start_pos
    for i in range(rows):
        for j in range(cols):
            if maze[i][j] == START:
                start_pos = (i, j)
                return True
    return False

def dfs(i, j):
    global current_exits
    if maze[i][j] == WALL or (i, j) in visited:
        return 0
    visited.append((i, j))
    exit_found = 1 if maze[i][j] == EXIT else 0
    current_exits += exit_found
    temp_style = {
        'fill': '#9b59b6' if not exit_found else '#27ae60',
        'outline': '#8e44ad' if not exit_found else '#2ecc71',
        'width': 4
    }
    x1, y1 = j * cell_size, i * cell_size
    x2, y2 = x1 + cell_size, y1 + cell_size
    canvas.create_rectangle(x1 + 1, y1 + 1, x2 - 1, y2 - 1,
                           fill=temp_style['fill'],
                           outline=temp_style['outline'],
                           width=temp_style['width'])
    if exit_found:
        canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2,
                          text="✓",
                          fill="white",
                          font=('Arial', 14, 'bold'))
    canvas.update()
    root.after(40)

    draw_maze()

    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    for di, dj in directions:
        ni, nj = i + di, j + dj
        if 0 <= ni < rows and 0 <= nj < cols:
            exit_found += dfs(ni, nj)
    
    return exit_found

if find_start():
    draw_maze()
    root.after(500)
    found_exits = dfs(start_pos[0], start_pos[1])

    result_text = f"Поиск завершен. Найдено выходов:{found_exits}"
    result_label = tk.Label(root, text=result_text, font=('Arial', 14, 'bold'),
                           bg='#1a1a1a', fg='#2ecc71')
    result_label.pack(pady=10)

root.mainloop()