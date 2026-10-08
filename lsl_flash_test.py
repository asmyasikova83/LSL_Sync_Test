"""
Flashes the screen white/black and pushes an LSL marker at each transition
"""

import time
import random
import tkinter as tk
from pylsl import StreamInfo, StreamOutlet, local_clock

N_FLASHES = 25
FLASH_HOLD = 0.40           # seconds the screen stays white
GAP_MIN, GAP_MAX = 1.2, 2.8  # random dark gap
SEED = 7                    # reproducible gaps

info = StreamInfo('FlashTest', 'Markers', 1, 0, 'string', 'flashtest-neuropc-1')
outlet = StreamOutlet(info)

root = tk.Tk()
root.title('FlashTest')
root.attributes('-fullscreen', True)
root.configure(bg='black')
root.config(cursor='none')
canvas = tk.Canvas(root, bg='black', highlightthickness=0)
canvas.pack(fill='both', expand=True)

state = {'abort': False}
root.bind('<Escape>', lambda e: state.update(abort=True))


def paint(colour):
    canvas.configure(bg=colour)
    root.update_idletasks()
    root.update()
    return local_clock()


def run():
    rng = random.Random(SEED)
    log = []
    canvas.configure(bg='black')
    root.update()
    time.sleep(2.0)

    for i in range(N_FLASHES):
        if state['abort']:
            break
        t_on = paint('white')
        outlet.push_sample(['flash_on'])
        time.sleep(FLASH_HOLD)

        t_off = paint('black')
        outlet.push_sample(['flash_off'])
        log.append((i, t_on, t_off))
        print(f'flash {i+1:2d}/{N_FLASHES}  on={t_on:.4f}  off={t_off:.4f}')

        gap = rng.uniform(GAP_MIN, GAP_MAX)
        end = time.perf_counter() + gap
        while time.perf_counter() < end:
            if state['abort']:
                break
            root.update()
            time.sleep(0.005)

    print(f'\ndone: {len(log)} flashes pushed on stream "FlashTest"')
    root.destroy()


root.after(200, run)
root.mainloop()