# Erdős #1108: p-е степени (p — нечётное простое) среди сумм факториалов различных чисел
# (0! и 1! различны). Тот же метод окна, что в e1108.py: s^p в [H, H+Lmax].
# Чётные степени уже покрыты квадратами (e1108.py), составные нечётные — своими простыми делителями.
# Запуск: python e1108_pow.py NMAX [процессов]   (контроль: python e1108_pow.py --control)
import sys, math, time
from multiprocessing import Pool
from e1108 import F, low_ok

PRIMES = [p for p in range(3, 700) if all(p % q for q in range(2, int(p ** 0.5) + 1))]


def iroot(n, b):
    # наибольшее x с x^b <= n
    if n < 2:
        return n
    x = 1 << ((n.bit_length() + b - 1) // b)   # x^b >= n
    while True:
        y = ((b - 1) * x + n // x ** (b - 1)) // b
        if y >= x:
            break
        x = y
    while x ** b > n:
        x -= 1
    while (x + 1) ** b <= n:
        x += 1
    return x


def choose_k(N, b):
    best = None
    for k in range(2, N + 1):
        lmax = sum(F[:k])
        width = lmax / (b * iroot(F[N], b) ** (b - 1) + 1)
        cost = 2 ** (N - k) * (1.0 + width)
        if best is None or cost < best[0]:
            best = (cost, k)
    return best[1]


def task(args):
    N, b, k, top_bits, top_val = args
    pos = list(range(k, N))
    free = pos[: len(pos) - top_bits]
    fixed = pos[len(pos) - top_bits:]
    H = F[N] + sum(F[p] for j, p in enumerate(fixed) if (top_val >> j) & 1)
    lmax = sum(F[:k])
    found = []
    for g in range(1 << len(free)):
        if g:
            bb = (g & -g).bit_length() - 1
            if ((g ^ (g >> 1)) >> bb) & 1:
                H += F[free[bb]]
            else:
                H -= F[free[bb]]
        hi = iroot(H + lmax, b)
        if hi ** b < H:
            continue
        lo = iroot(H - 1, b) + 1
        for s in range(lo, hi + 1):
            if low_ok(s ** b - H, k):
                found.append(s ** b)
    return found, 1 << len(free)


def direct_task(args):
    # мало кандидатов s: проверяем каждое s^b в [N!, N! + сумма (N-1)!..0!] целиком
    N, b = args[0], args[1]
    lo = iroot(F[N] - 1, b) + 1
    hi = iroot(F[N] + sum(F[:N]), b)
    found = [s ** b for s in range(max(lo, 2), hi + 1) if low_ok(s ** b - F[N], N)]
    return found, hi - lo + 1 if hi >= lo else 0


def run(args):
    return direct_task(args) if args[2] == "direct" else task(args)


DIRECT = 0


def search(nmax, procs, nmin=2):
    global DIRECT
    tasks = []
    for N in range(nmin, nmax + 1):
        for b in PRIMES:
            if 2 ** b > 2 * F[N] + 2:     # s >= 2 даёт s^b > любой суммы с наибольшим N!
                break
            k = choose_k(N, b)
            nd = iroot(F[N] + sum(F[:N]), b) - iroot(F[N] - 1, b)
            if nd <= 2 ** (N - k):
                tasks.append((N, b, "direct"))
                DIRECT += 1
                continue
            tb = min(N - k, 8)
            for v in range(1 << tb):
                tasks.append((N, b, k, tb, v))
    res = set()
    total = 0
    t0 = time.time()
    with Pool(procs) as pool:
        for found, n in pool.imap_unordered(run, tasks, chunksize=4):
            total += n
            res.update(found)
    return res, total, time.time() - t0


def brute(nmax):
    vals = {0}
    for i in range(0, nmax + 1):
        vals |= {v + F[i] for v in vals}
    out = set()
    for v in vals:
        if v < 2:
            continue
        for b in PRIMES:
            if 2 ** b > v:
                break
            r = iroot(v, b)
            if r ** b == v:
                out.add(v)
                break
    return out


if __name__ == "__main__":
    if sys.argv[1] == "--control":
        nm = 18
        bset = brute(nm)
        s, tot, dt = search(nm, 8)
        print("контроль до %d!: перебор всех подмножеств %d нечётных простых степеней, окно %d, совпадают: %s"
              % (nm, len(bset), len(s), bset == s))
        print("найдено:", sorted(s), "прямых задач (N,b):", DIRECT)
        sys.exit(0 if bset == s else 1)
    nmax = int(sys.argv[1]); procs = int(sys.argv[2]) if len(sys.argv) > 2 else 16
    nmin = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    s, tot, dt = search(nmax, procs, nmin)
    print("N %d..%d: H перебрано %d за %.0f с" % (nmin, nmax, tot, dt))
    print("нечётных простых степеней %d; наибольшая %s" % (len(s), max(s) if s else None))
    print("все:", sorted(s), "прямых задач (N,b):", DIRECT)
