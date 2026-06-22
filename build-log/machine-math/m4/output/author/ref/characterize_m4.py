"""Characterization script for Machine Math M4.

Runs all three major artifacts and prints real measured numbers:
- Single DecisionTreeRegressor vs mean baseline (test MSE)
- Single DecisionTreeClassifier vs RandomForestClassifier vs sklearn RF (test accuracy)
- GradientBoostingRegressor: test R^2 + train loss at rounds 1, 10, 25, 50, 75, 100
- Tradeoff sweep: tuned vs overfit config (train MSE and test MSE)

No sklearn inside the algorithms. Numbers are measured, not estimated.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

import numpy as np
from sklearn.datasets import load_breast_cancer, make_friedman1
from sklearn.ensemble import GradientBoostingRegressor as SklearnGB
from sklearn.ensemble import RandomForestClassifier as SklearnRF
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier as SklearnDTC
from sklearn.tree import DecisionTreeRegressor as SklearnDTR

from ml.ensemble import GradientBoostingRegressor, RandomForestClassifier
from ml.tree import DecisionTreeClassifier, DecisionTreeRegressor


def r2(y_true, y_pred):
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return float(1.0 - ss_res / ss_tot)


def mse(y_true, y_pred):
    return float(np.mean((y_true - y_pred) ** 2))


print("=" * 64)
print("SECTION 1: DecisionTreeRegressor -- 1-D sine signal")
print("=" * 64)

rng = np.random.default_rng(42)
n = 200
X_reg = rng.uniform(0, 2 * np.pi, size=(n, 1))
y_reg = np.sin(X_reg[:, 0]) + rng.normal(0, 0.1, size=n)
X_tr_r, X_te_r, y_tr_r, y_te_r = train_test_split(X_reg, y_reg, test_size=0.2, random_state=0)

baseline_mse = mse(y_te_r, np.full_like(y_te_r, np.mean(y_tr_r)))

for depth in [2, 4, 6]:
    reg = DecisionTreeRegressor(max_depth=depth).fit(X_tr_r, y_tr_r)
    sk_reg = SklearnDTR(max_depth=depth, random_state=0).fit(X_tr_r, y_tr_r)
    corr = float(np.corrcoef(reg.predict(X_te_r), sk_reg.predict(X_te_r))[0, 1])
    print(f"  max_depth={depth}: scratch test MSE={mse(y_te_r, reg.predict(X_te_r)):.4f}  "
          f"sklearn MSE={mse(y_te_r, sk_reg.predict(X_te_r)):.4f}  corr={corr:.4f}")

print(f"  Mean-baseline test MSE: {baseline_mse:.4f}")

print()
print("=" * 64)
print("SECTION 2: RandomForestClassifier -- breast_cancer")
print("=" * 64)

X_c, y_c = load_breast_cancer(return_X_y=True)
X_tr_c, X_te_c, y_tr_c, y_te_c = train_test_split(
    X_c, y_c, test_size=0.2, stratify=y_c, random_state=0
)

MAX_DEPTH = 6
N_EST = 100

single = DecisionTreeClassifier(max_depth=MAX_DEPTH).fit(X_tr_c, y_tr_c)
rf = RandomForestClassifier(n_estimators=N_EST, max_depth=MAX_DEPTH, random_state=0).fit(X_tr_c, y_tr_c)
sk_rf = SklearnRF(n_estimators=N_EST, max_depth=MAX_DEPTH, random_state=0).fit(X_tr_c, y_tr_c)
sk_single = SklearnDTC(max_depth=MAX_DEPTH, random_state=0).fit(X_tr_c, y_tr_c)

acc_single = float(np.mean(single.predict(X_te_c) == y_te_c))
acc_rf = float(np.mean(rf.predict(X_te_c) == y_te_c))
acc_sk_rf = float(np.mean(sk_rf.predict(X_te_c) == y_te_c))
acc_sk_single = float(np.mean(sk_single.predict(X_te_c) == y_te_c))
rf_sk_agree = float(np.mean(rf.predict(X_te_c) == sk_rf.predict(X_te_c)))

print(f"  Single tree (scratch, max_depth={MAX_DEPTH}): test acc = {acc_single:.4f}")
print(f"  Single tree (sklearn, max_depth={MAX_DEPTH}): test acc = {acc_sk_single:.4f}")
print(f"  RandomForest (scratch, n={N_EST}, max_depth={MAX_DEPTH}): test acc = {acc_rf:.4f}")
print(f"  RandomForest (sklearn, n={N_EST}, max_depth={MAX_DEPTH}): test acc = {acc_sk_rf:.4f}")
print(f"  Scratch RF vs sklearn RF label agreement: {rf_sk_agree:.4f}")

print()
print("=" * 64)
print("SECTION 3: GradientBoostingRegressor -- friedman1")
print("=" * 64)

X_gb, y_gb = make_friedman1(n_samples=500, n_features=10, noise=1.0, random_state=0)
X_tr_gb, X_te_gb, y_tr_gb, y_te_gb = train_test_split(X_gb, y_gb, test_size=0.2, random_state=0)

gbr = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=3).fit(X_tr_gb, y_tr_gb)
sk_gbr = SklearnGB(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=0).fit(X_tr_gb, y_tr_gb)

test_r2_scratch = r2(y_te_gb, gbr.predict(X_te_gb))
test_r2_sk = r2(y_te_gb, sk_gbr.predict(X_te_gb))
pred_corr = float(np.corrcoef(gbr.predict(X_te_gb), sk_gbr.predict(X_te_gb))[0, 1])

print(f"  Scratch GBR test R^2: {test_r2_scratch:.4f}")
print(f"  Sklearn  GBR test R^2: {test_r2_sk:.4f}")
print(f"  Prediction correlation (scratch vs sklearn): {pred_corr:.4f}")
print()
print("  Train loss across rounds (scratch GBR):")
for rnd in [1, 5, 10, 25, 50, 75, 100]:
    idx = rnd - 1
    print(f"    round {rnd:3d}: train MSE = {gbr.train_losses_[idx]:.4f}")

print()
print("=" * 64)
print("SECTION 4: Tradeoff sweep -- overfit vs tuned config")
print("=" * 64)

X_sw, y_sw = make_friedman1(n_samples=300, n_features=10, noise=1.0, random_state=0)
X_tr_sw, X_te_sw, y_tr_sw, y_te_sw = train_test_split(X_sw, y_sw, test_size=0.2, random_state=0)

tuned_gbr = GradientBoostingRegressor(n_estimators=50, learning_rate=0.05, max_depth=3).fit(X_tr_sw, y_tr_sw)
overfit_gbr = GradientBoostingRegressor(n_estimators=200, learning_rate=0.5, max_depth=8).fit(X_tr_sw, y_tr_sw)

print(f"  TUNED   config (n=50, lr=0.05, depth=3):")
print(f"    train MSE (final round): {tuned_gbr.train_losses_[-1]:.4f}")
print(f"    test  MSE:               {mse(y_te_sw, tuned_gbr.predict(X_te_sw)):.4f}")
print(f"    test  R^2:               {r2(y_te_sw, tuned_gbr.predict(X_te_sw)):.4f}")
print()
print(f"  OVERFIT config (n=200, lr=0.5, depth=8):")
print(f"    train MSE (final round): {overfit_gbr.train_losses_[-1]:.4f}")
print(f"    test  MSE:               {mse(y_te_sw, overfit_gbr.predict(X_te_sw)):.4f}")
print(f"    test  R^2:               {r2(y_te_sw, overfit_gbr.predict(X_te_sw)):.4f}")
print()
print(f"  Overfit early train loss (rounds 1-10 avg): {float(np.mean(overfit_gbr.train_losses_[:10])):.4f}")
print(f"  Overfit late  train loss (rounds 191-200 avg): {float(np.mean(overfit_gbr.train_losses_[-10:])):.4f}")
print()
print("Done.")
