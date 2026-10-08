import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
#import Path

r = 177
counter = 0
ampl = 'NVX52'
dir_path = fr"\\MCSSERVER\DB Temp\msasha\LSL_VR_triggers\{ampl}\upd"
dir_stat = fr"\\MCSSERVER\DB Temp\msasha\LSL_VR_triggers\{ampl}\stat_{ampl}\upd"
dir_pic = fr"\\MCSSERVER\DB Temp\msasha\LSL_VR_triggers\{ampl}\pic_{ampl}\upd"
os.makedirs(dir_stat, exist_ok=True)
os.makedirs(dir_pic, exist_ok=True)

general_lags = []

for num in range(r):

    fname = os.path.join(dir_path, f"out_{ampl}_test_{num}.txt")
    if not os.path.isfile(fname):
        print(f"Файл не найден: {fname}")
    else:
        df = pd.read_csv(
        fname,
        sep=r'\s+',
        header=None,
        encoding='utf-8',
        names=['time', 'event'],
        on_bad_lines='skip'
        )
        print(df)

        t0 = df['time'].iloc[0]
        print(t0)
        df['t_rel'] = df['time'] - t0  # 0, 0.0055, 0.0555, ...
        flash_mask = df['event'] == 'flash_on'
        nvx_mask = df['event'] == '14'

        flash_df_idx = df.index[flash_mask].to_numpy()
        nvx_df_idx = df.index[nvx_mask].to_numpy()

        flash_times = df.loc[flash_mask, 't_rel'].to_numpy()
        print('len flash_times', len(flash_times))
        nvx_times = df.loc[nvx_mask, 't_rel'].to_numpy()

        # Создаём колонку, заполняем NaN
        df['t_diff'] = np.nan

        for i, ft in enumerate(flash_times):
            pos = np.searchsorted(nvx_times, ft, side='left')

            if pos < len(nvx_times):
                lag = nvx_times[pos] - ft
                # Пишем лаг в строку flash_on (в секундах)
                df.loc[flash_df_idx[i], 't_diff'] = lag

        print(df.loc[flash_mask, ['t_rel', 'event', 't_diff']].head(15))

        # Статистика в мс
        lags = (
            df.loc[flash_mask, 't_diff']  # выбираем колонку по маске
            .dropna()  # убираем пропуски
            .to_numpy()  # конвертируем в numpy-массив
        )

        if  len(flash_times) == 25:
            counter += 1
            general_lags.append(lags)

general_lags_arr = np.array(general_lags).flatten()

print('Min diff: ', np.round(min(general_lags_arr), 4), 'sec' )
print('Max diff: ', np.round(max(general_lags_arr), 4), 'sec' )
print('Mean diff: ', np.round(np.mean(general_lags_arr), 4), 'sec')

min_diff = np.float64(np.min(general_lags_arr))
print(f"Min diff: {min_diff:.6e}   sec")
max_diff = np.max(general_lags_arr)
mean_diff = np.mean(general_lags_arr)

# Формируем текст для файла (как твои print, но в строку)
content = (
        f"Min diff: {min_diff}\n"
        f"Max diff: {max_diff}\n"
        f"Mean diff: {mean_diff}\n"
        )

fname = os.path.join(dir_stat, f"total_stat_{ampl}_{counter}_ed.txt")
#    Сохраняем в .txt
with open(fname, 'w', encoding='utf-8') as f:
        f.write(content)
print(f"Статистика сохранена в: {fname}")

fig, ax = plt.subplots(figsize=(10, 6))

# Boxplot
bp = ax.boxplot(
        lags,
        orientation='vertical',
        patch_artist=True,
        widths=0.4
        )

for patch in bp['boxes']:
    patch.set_facecolor('#4c72b0')
    patch.set_edgecolor('black')

for element in ['whiskers', 'caps', 'medians', 'fliers']:
    for line in bp[element]:
        line.set_color('black')
        if element == 'medians':
            line.set_linewidth(2)
            line.set_label(f'Медиана: {np.median(lags) :.4f} сeкунды')

ax.set_title(f'Boxplot лагов между flash_on и первым триггером NeoRec-{ampl} runs:{counter}', fontsize=16)
ax.set_ylabel('Лаг (секунды)', fontsize=16)
ax.set_xlabel('')
ax.tick_params(axis='both', which='major', labelsize=16)
ax.legend(loc='upper right')
ax.grid(axis='y', linestyle='--', alpha=0.3)

plt.tight_layout()
fname = os.path.join(dir_pic, f"lag_{ampl}_runs_{counter}.png")
plt.savefig(fname, dpi=300, bbox_inches='tight')
print(f"График сохранён в текущей папке как: {fname}")
