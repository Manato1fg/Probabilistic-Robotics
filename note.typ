#import "template.typ": *

#let writeDate = datetime(
  year: 2024,
  month: 2,
  day: 9
)

#show: report.with(
  title: "詳解 確率ロボティクス メモ",
  date: writeDate,
  author: "Manato1fg",
  //affiliation: "東京大学工学部計数工学科システム情報コース 3年"
)

= 第一章
省略

= 第二章

#theorem("中心極限定理")[
  ある確率分布$P$にしたがう確率変数$X_1, X_2, ... X_N$に対し，確率変数$Y$を次のように定義する．
  $
  Y = (X_1 + X_2 + dots.h.c + X_N) / sqrt(N)
  $
  このとき，$Y$は$N$が十分大きくなると正規分布に収束する．
]

#proof[
  特性関数を用いた厳密でない証明を行う．\
  特性関数$Theta(j u)$は以下のように定義される．
  $
  Theta(j u) = bb(E)[e^(j u x)] = integral_(-oo)^(oo) e^(j u x) p(x) dif x
  $
  ここで，$p(x)$は確率変数$X$の確率密度関数である．

  確率変数の和で定義される確率変数の計算の際に畳み込み演算をすることに注意して，確率変数$Z$を
  $
  Z = X_1 + X_2 + dots.h.c + X_N
  $
  とすると，重畳積分定理から$Z$の特性関数$Theta_z (j u)$は次のようになる．
  $
  Theta_z (j u) = (Theta(j u))^N
  $
  
  また，$display(Y = Z / sqrt(N))$と定義すると，$Y$の特性関数$Theta_y (j u)$は次のようになる．
  $
  Theta_y (j u) = Theta_z (j sqrt(N) u) = (Theta((j u) / sqrt(N)))^N
  $

  キュムラントと特性関数の関係から，
  $
  log(Theta_y(j u)) &= N log(Theta((j u) / sqrt(N))) \
  &= sum_(n = 1)^(oo) (N k_n) / N^(n/2) (j u)^n / n!
  $
  となる．ここで，$k_n$は確率変数$X$の$n$次のキュムラントである．

  $n gt.eq 3$の項は$N$が十分大きくなるにつれて$0$に収束する．よって，$Y$の三次以上のキュムラントは$0$であり，定義から$Y$は正規分布に収束する．
]

#corollary[
  $
  Y = (sum_(n=1)^N X_n - mu) / (sqrt(N) sigma)
  $
  とおけば，$Y$は標準正規分布に収束する．
]

#figure(
  grid(
    columns: 2,
    image("./2/n_1.png"), image("./2/n_10.png"),
    "N = 1", "N = 10",
    image("./2/n_100.png"), image("./2/n_1000.png"),
    "N = 100", "N = 1000"
  ),
  caption: "中心極限定理のシミュレーション",
)