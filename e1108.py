# Erdős #1108: квадраты, равные сумме факториалов различных чисел (0! и 1! различны, как в A025494).
# Метод: сумма с наибольшим слагаемым N! = H + L, H = N! + (подмножество {k!..(N-1)!}),
# L — подмножество {0!..(k-1)!}, 0 <= L <= Lmax. Квадрат s^2 обязан лежать в [H, H+Lmax]:
# перебираем s от ceil(sqrt H) до isqrt(H+Lmax) и проверяем, что s^2-H раскладывается в 0/1-цифры
# факториальной системы на позициях < k. k(N) выбираем, чтобы окно было почти всегда пустым.
# Запуск: python e1108.py NMAX [процессов]   (контроль: python e1108.py --control)
import sys, math, time
from multiprocessing import Pool

NF = 200
F = [1] * (NF + 1)
for i in range(1, NF + 1):
    F[i] = F[i - 1] * i


def digits_ok(x, k):
    # x = сумма различных i! при 1 <= i <= k-1 ?
    i = 2
    while x:
        if i > k:          # цифра на позиции >= k
            return False
        d = x % i
        if d > 1:
            return False
        x //= i
        i += 1
    return True


def low_ok(L, k):
    # L = (0 или 0!) + сумма различных i!, 1 <= i <= k-1
    if L < 0:
        return False
    return digits_ok(L, k) or (L >= 1 and digits_ok(L - 1, k))


def choose_k(N):
    best = None
    for k in range(2, N + 1):
        lmax = sum(F[:k])
        cost = 2 ** (N - k) * (1.0 + lmax / (2.0 * math.isqrt(F[N]) + 1))
        if best is None or cost < best[0]:
            best = (cost, k)
    return best[1]


def task(args):
    N, k, top_bits, top_val = args
    # позиции k..N-1; старшие top_bits из них фиксированы значением top_val
    pos = list(range(k, N))
    free = pos[: len(pos) - top_bits]
    fixed = pos[len(pos) - top_bits:]
    H = F[N] + sum(F[p] for j, p in enumerate(fixed) if (top_val >> j) & 1)
    lmax = sum(F[:k])
    found = []
    nfree = len(free)
    isqrt = math.isqrt
    cnt = 0
    for g in range(1 << nfree):
        if g:
            b = (g & -g).bit_length() - 1   # Грей: меняется бит b
            if ((g ^ (g >> 1)) >> b) & 1:
                H += F[free[b]]
            else:
                H -= F[free[b]]
        hi = isqrt(H + lmax)
        if hi * hi < H:
            continue
        lo = isqrt(H - 1) + 1
        for s in range(lo, hi + 1):
            if low_ok(s * s - H, k):
                found.append(s)
        cnt += 1
    return N, found, 1 << nfree, cnt


def search(nmax, procs, nmin=2):
    tasks = []
    for N in range(nmin, nmax + 1):
        k = choose_k(N)
        width = N - k
        tb = min(width, 8)
        for v in range(1 << tb):
            tasks.append((N, k, tb, v))
    # наибольшее слагаемое 0! или 1!: суммы 1 и 2, квадрат только 1
    squares = {1} if nmin <= 2 else set()
    total = 0
    t0 = time.time()
    with Pool(procs) as pool:
        for N, found, n, _ in pool.imap_unordered(task, tasks, chunksize=1):
            total += n
            for s in found:
                squares.add(s * s)
    return squares, total, time.time() - t0


def brute(nmax):
    # независимый прибор: все подмножества {0!,1!,...,nmax!}
    vals = {0}
    for i in range(0, nmax + 1):
        vals |= {v + F[i] for v in vals}
    return {v for v in vals if v > 0 and math.isqrt(v) ** 2 == v}


KNOWN = [1, 4, 9, 25, 121, 144, 729, 841, 5041, 5184, 45369, 46225, 363609, 403225, 3674889]

if __name__ == "__main__":
    if sys.argv[1] == "--control":
        nm = 18
        b = brute(nm)
        s, tot, dt = search(nm, 8)
        print("контроль перебор всех подмножеств до %d!: %d квадратов; метод окна: %d; совпадают: %s"
              % (nm, len(b), len(s), b == s))
        print("известные члены A025494 (первые 15) найдены методом: %d из %d" % (len([x for x in KNOWN if x in s]), len(KNOWN)))
        print("отличия:", sorted(b ^ s)[:5])
        sys.exit(0 if b == s else 1)
    nmax = int(sys.argv[1]); procs = int(sys.argv[2]) if len(sys.argv) > 2 else 16
    nmin = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    s, tot, dt = search(nmax, procs, nmin)
    print("N %d..%d: H перебрано %d за %.0f с" % (nmin, nmax, tot, dt))
    print("квадратов найдено %d; наибольший %s" % (len(s), max(s) if s else None))
    print("все:", sorted(s))
