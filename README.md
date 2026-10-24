# Erdős Problem #1108: perfect powers among sums of distinct factorials

**AI disclosure.** The method, code and runs were produced by an AI system (Claude, Anthropic) working for AEVION. They were checked by the controls listed below, not by a human proof. Published by Dosymbek Zhaqiya (AEVION), October 2026.

Problem (erdosproblems.com/1108): A = { sum over n in S of n! : S a finite set of naturals, with 0! and 1! counted as distinct terms }. Does A contain only finitely many k-th powers (k ≥ 2)? Only finitely many powerful numbers?

## Results

| Claim | Bound | Previously stated |
|---|---|---|
| The only squares in A are the 16 known ones (OEIS A025494, largest 1183893² = 1401602635449) | below 81! ≈ 5.80·10¹²⁰ | 48! ≈ 1.24·10⁶¹ (J. E. Schoenfield, 2006) |
| The only p-th powers (p an odd prime) in A are 8, 27, 32, 128, 729 | below 101! ≈ 9.43·10¹⁵⁹ | — |

Every perfect power is a square or a p-th power for some odd prime p. So the perfect powers in A below 81! are exactly the 16 squares together with 8, 27, 32 and 128 (729 = 27² is among the squares).

Not covered: powerful numbers (OEIS A115645), because a powerful number need not be a perfect power.

## Method

Write an element of A whose largest term is N! as H + L. Here H = N! + (sum of a subset of {k!, …, (N−1)!}) and 0 ≤ L ≤ L_max = Σ_{i<k} i!.

If H + L = s^p, then s lies between ⌈H^{1/p}⌉ and ⌊(H + L_max)^{1/p}⌋. When k is chosen with k! of order p·H^{1−1/p}, this window is almost always empty. For every candidate s, the program checks that s^p − H (or s^p − H − 1, which covers the term 0!) has factorial-base digits in {0, 1} at all positions below k.

H runs over its 2^{N−k} values in Gray-code order, and k(N, p) is chosen to minimise the total work. For large p there are fewer candidates s with s^p in [N!, N! + Σ_{i<N} i!] than there are values of H. In that case each such s^p is tested directly.

## Controls (re-run inside this package, 24.10.2026)

- `python e1108.py --control`: the method finds the first 15 terms of A025494 (15 of 15); see `logs/control_squares.txt`.
- `python e1108_pow.py --control`: brute force over all 2¹⁹ subsets of {0!, …, 18!} gives 5 odd prime powers, and the method gives the same 5; see `logs/control_odd.txt`.
- Squares were also checked against brute force over all subsets of {0!, …, 20!} (16 = 16), and the 2006 result up to 48! was reproduced exactly (`logs/e1108_48.txt`).
- Mutation tests: each deliberately broken version was caught by the controls. The breaks were the digit bound, the window edges, the Gray-code step, and the upper edge and digit bound of the direct path.

## Runs (logs/)

| File | Range | Values checked | Found |
|---|---|---|---|
| e1108_48.txt | squares, N ≤ 48 | 1 648 936 | 16 (the known ones) |
| e1108_49_70.txt | squares, 49 ≤ N ≤ 70 | 1 110 441 984 | 0 |
| e1108_71_76.txt | squares, 71 ≤ N ≤ 76 | 5 637 144 576 | 0 |
| e1108_77.txt … e1108_80.txt | squares, N = 77, 78, 79, 80 | 2³¹, 2³¹, 2³², 2³² | 0 |
| e1108_pow_70.txt | odd prime powers, N ≤ 70 | 1 432 579 | 5 |
| e1108_pow_71_100.txt | odd prime powers, 71 ≤ N ≤ 100 | 491 098 097 | 0 |

Usage: `python e1108.py NMAX [processes] [NMIN]` and `python e1108_pow.py NMAX [processes] [NMIN]`. The scripts need Python 3.8 or later and no other packages. File integrity: `SHA256SUMS`.
