# サイコロを振ったときに中心極限定理が成立するかを見る

import numpy as np
import matplotlib.pyplot as plt

for n in [1, 10, 100, 1000]:
    history = []
    y_list = np.zeros(6 * n + 1, dtype=int)
    # サイコロをn回振る試行を10000回行う
    for i in range(10000):
        dice = np.random.randint(1, 7, n)
        # サイコロの目の合計を求める
        y = np.sum(dice)
        y_list[y] += 1
        history.append(y)

    # 平均
    mean = np.mean(history)
    # 分散
    var = np.var(history)

    x = np.linspace(np.min(history), np.max(history), 10000)
    p = 1 / np.sqrt(2 * np.pi * var) * np.exp(-(x - mean)**2 / (2 * var))
    # 棒グラフを描画
    plt.bar(range(6 * n + 1), y_list / 10000, color='blue')
    # 確率密度関数を描画
    plt.plot(x, p, color='red')
    plt.title(f'n = {str(n)}, mean = {mean:.2f}, var = {var:.2f}')
    plt.xlim([np.min(history), np.max(history)])

    plt.legend(['p(x)', 'simulation'])

    plt.show()
