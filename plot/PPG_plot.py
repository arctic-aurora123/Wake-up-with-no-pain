import pandas as pd
import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt
import scipy.stats as stats
import seaborn as sns

sample_rate = 256

plt.figure(figsize=(12, 6))
df_values = pd.DataFrame(columns=['mean', 'max', 'delta','label'])
    
for idx in range(24):
    df = pd.read_csv(f"data/heart_rate{idx}.csv")
    start = 0
    
    df =  df.iloc[start:-1]
    
    ppg_data = df['PPG_analog'].values
    df['time_ms'] /= 1000
    fs = sample_rate  # replace with your sampling frequency

    # 1. Preprocessing
    # Remove DC component
    ppg_data = ppg_data - np.mean(ppg_data)
    # Low-pass filter
    low_cutoff = 2.5 # 2.5 Hz
    b, a = signal.butter(3, low_cutoff / (0.5 * fs), btype='low')
    ppg_low = signal.filtfilt(b, a, ppg_data)

    # High-pass filter
    high_cutoff = 0.5  # 0.5 Hz
    b, a = signal.butter(3, high_cutoff / (0.5 * fs), btype='high')
    ppg_filtered = signal.filtfilt(b, a, ppg_low)

    # 2. Smoothing
    ppg_smoothed = signal.savgol_filter(ppg_filtered, window_length=51, polyorder=3)

    # 3. Segment the data into windows
    window_size = fs * 60  # 60 seconds window
    step_size = fs * 1     # 1 seconds step
    num_windows = (len(ppg_smoothed) - window_size) // step_size + 1

    heart_rates = []

    for i in range(num_windows):
        start = i * step_size
        end = start + window_size
        window_data = ppg_smoothed[start:end]

        # 4. Peak Detection in the window
        peaks, _ = signal.find_peaks(window_data, distance=fs*0.6)  # minimum distance of 0.6 seconds between peaks

        if len(peaks) > 1:
            # 5. Heart Rate Calculation for the window
            ibi = np.diff(peaks) / fs  # Inter-beat intervals in seconds
            bpm = 60 / ibi  # Convert to beats per minute
            heart_rate = np.mean(bpm)
        else:
            heart_rate = np.nan  # Handle cases with not enough peaks

        heart_rates.append(heart_rate)

    # Convert the heart rate list to a numpy array
    heart_rates = np.array(heart_rates)

    # Smooth the heart rate values using a Savitzky-Golay filter
    smoothed_heart_rates = signal.savgol_filter(heart_rates, window_length=10, polyorder=3)
    mean = smoothed_heart_rates[0:100].mean()

    max = smoothed_heart_rates.max()
    delta = max - mean
    # Plot the heart rate over time
    time = np.arange(num_windows) * step_size / fs
    
    plt.plot(time, smoothed_heart_rates, label=f'participant{idx}')
    df_values.loc[idx,'mean'] = mean
    df_values.loc[idx,'max'] = max
    df_values.loc[idx,'delta'] = delta

harsh = [1, 3, 5, 6, 7, 8, 10, 11, 19, 20, 21, 22]
natural = [0, 2, 4, 9, 12, 13, 14, 15, 16, 17, 18, 23]
for i in harsh:
    df_values.loc[i, 'label'] = 'harsh'
for i in natural:
    df_values.loc[i, 'label'] = 'natural'
    
print(df_values)
df_values.to_csv('./data/heart_rate_values.csv')
plt.title('Heart Rate over Time')
plt.xlabel('Time (seconds)')
plt.ylabel('Heart Rate (BPM)')
plt.legend()
# plt.show()

palette = sns.color_palette("muted", 2)
fig, ax = plt.subplots()
sns.boxplot(x='label', y='delta', data=df_values, palette=palette, ax=ax, showmeans=True, meanline=True)


plt.title('Heart Rate Differences', size=12) 
plt.ylabel('Difference in heart rate',size=10) 
plt.xlabel('Alarm clock sound',size=10) 

plt.show()
harsh = df_values.loc[[1, 3, 5, 6, 7, 8, 10, 11, 19, 20, 21, 22], 'delta']
natural = df_values.loc[[0, 2, 4, 9, 12, 13, 14, 15, 16, 17, 18, 23], 'delta']
t_result = stats.ttest_rel(harsh, natural)
print(t_result)
