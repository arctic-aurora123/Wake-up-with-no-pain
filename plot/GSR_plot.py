import pandas as pd
import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt
import scipy.stats as stats
import seaborn as sns

sample_rate = 256

plt.figure(figsize=(12, 6))
df_values = pd.DataFrame(columns=['mean', 'min', 'delta'])
for idx in range(24):
    df = pd.read_csv(f"data/heart_rate{idx}.csv")
    
    gsr_data = df['GSR_analog'].values
    df['time_ms'] /= 1000
    fs = sample_rate  # replace with your sampling frequency

    # 2. Smoothing
    gsr_smoothed = signal.savgol_filter(gsr_data, window_length=100, polyorder=3)

    # 3. Segment the data into windows
    window_size = fs * 10  # 10 seconds window
    step_size = fs * 1     # 1 seconds step
    num_windows = (len(gsr_smoothed) - window_size) // step_size + 1

    gsr_value = []

    for i in range(num_windows):
        start = i * step_size
        end = start + window_size
        window_data = gsr_smoothed[start:end]

        gsr_value.append(window_data.mean())

    # Convert the heart rate list to a numpy array
    gsr_value = np.array(gsr_value)

    # Smooth the heart rate values using a Savitzky-Golay filter
    smoothed_gsr_value = signal.savgol_filter(gsr_value, window_length=100, polyorder=3)
    mean =  smoothed_gsr_value[0:50].mean()
    min = smoothed_gsr_value.min()
    delta = mean - min
    # Plot the heart rate over time
    time = np.arange(num_windows) * step_size / fs
    
    plt.plot(time, gsr_value, label=f'participant{idx}')
    df_values.loc[len(df_values)] = [mean, min, delta]

harsh = [1, 3, 5, 6, 7, 8, 10, 11, 19, 20, 21, 22]
natural = [0, 2, 4, 9, 12, 13, 14, 15, 16, 17, 18, 23]
for i in harsh:
    df_values.loc[i, 'label'] = 'harsh'
for i in natural:
    df_values.loc[i, 'label'] = 'natural'
print(df_values)
df_values.to_csv('./data/gsr_values.csv')

plt.title('GSR over Time')
plt.xlabel('Time (seconds)')
plt.ylabel('GSR Value')
plt.legend()

palette = sns.color_palette("muted", 2)
fig, ax = plt.subplots()
sns.boxplot(x='label', y='delta', data=df_values, palette=palette, ax=ax, showmeans=True, meanline=True)

plt.title('GSR Differences', size=12) 
plt.ylabel('Difference in GSR',size=10) 
plt.xlabel('Alarm clock sound',size=10)  

plt.show()
harsh = df_values.loc[[1, 3, 5, 6, 7, 8, 10, 11, 19, 20, 21, 22], 'delta']
natural = df_values.loc[[0, 2, 4, 9, 12, 13, 14, 15, 16, 17, 18, 23], 'delta']
t_result = stats.ttest_rel(harsh, natural)
print(t_result)