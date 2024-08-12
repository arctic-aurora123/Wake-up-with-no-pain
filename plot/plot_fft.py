import numpy as np
from scipy.io import wavfile
from scipy.fft import fft, fftfreq
import matplotlib.pyplot as plt

# 读取音频文件
rate1, audio1 = wavfile.read('birds.wav')
rate2, audio2 = wavfile.read('ocean.wav')
rate3, audio3 = wavfile.read('radar.wav')
rate4, audio4 = wavfile.read('old_ring.wav')

# 确保音频是单声道
audio1 = audio1.mean(axis=1) if audio1.ndim > 1 else audio1
audio2 = audio2.mean(axis=1) if audio2.ndim > 1 else audio2
audio3 = audio3.mean(axis=1) if audio3.ndim > 1 else audio3
audio4 = audio4.mean(axis=1) if audio4.ndim > 1 else audio4

# 应用FFT
fft1 = fft(audio1)
fft2 = fft(audio2)
fft3 = fft(audio3)
fft4 = fft(audio4)

# 计算频率轴
n1, n2, n3, n4 = len(audio1), len(audio2), len(audio3), len(audio4)
freqs1 = fftfreq(n1, 1/rate1)
freqs2 = fftfreq(n2, 1/rate2)
freqs3 = fftfreq(n3, 1/rate3)
freqs4 = fftfreq(n4, 1/rate4)

# 只取正频率部分
fft1 = np.abs(fft1[:n1//2])
fft2 = np.abs(fft2[:n2//2])
fft3 = np.abs(fft3[:n3//2])
fft4 = np.abs(fft4[:n4//2])
freqs1 = freqs1[:n1//2]
freqs2 = freqs2[:n2//2]
freqs3 = freqs3[:n3//2]
freqs4 = freqs4[:n4//2]

# 识别每组中振幅最大的两个频率及其索引
idx1 = np.argsort(fft1)[-2:][::-1]
idx2 = np.argsort(fft2)[-2:][::-1]
idx3 = np.argsort(fft3)[-2:][::-1]
idx4 = np.argsort(fft4)[-2:][::-1]

# 绘制频谱图
fig, axs = plt.subplots(1, 2, figsize=(10, 10))

# Natural Sounds
axs[0].plot(freqs1, fft1, label='Birds')
axs[0].plot(freqs2, fft2, label='Ocean')
for idx, color in zip([idx1, idx2], ['red', 'green']):
    max_freqs, max_ffts = freqs1[idx], fft1[idx]
    axs[0].scatter(max_freqs, max_ffts, color=color, label=f'Top 2 Frequencies {color}')
    for i, (freq, fft_val) in enumerate(zip(max_freqs, max_ffts)):
        axs[0].text(freq, fft_val, f'{int(freq):.0f} Hz', color=color, fontsize=9, ha='center', va='bottom')

axs[0].set_title('Natural Sounds Frequency Spectrum')
axs[0].legend()

# Harsh Sounds
axs[1].plot(freqs3, fft3, label='Radar')
axs[1].plot(freqs4, fft4, label='Old Ring')
for idx, color in zip([idx3, idx4], ['red', 'green']):
    max_freqs, max_ffts = freqs3[idx], fft3[idx]
    axs[1].scatter(max_freqs, max_ffts, color=color, label=f'Top 2 Frequencies {color}')
    for i, (freq, fft_val) in enumerate(zip(max_freqs, max_ffts)):
        axs[1].text(freq, fft_val, f'{int(freq):.0f} Hz', color=color, fontsize=9, ha='center', va='bottom')

axs[1].set_title('Harsh Sounds Frequency Spectrum')
axs[1].legend()

# 设置x轴显示范围
for ax in axs:
    ax.set_xlim(0, 6000)  # 可以根据需要调整这个值
    ax.grid(True)
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Amplitude')

plt.tight_layout()
plt.show()