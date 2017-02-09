# Critical Line Algorithm
# by MLdP <lopezdeprado@lbl.gov>
from __future__ import (absolute_import, division, print_function)
#                     , unicode_literals)   # needs to be disable for np.array(..., dtype=...) below
import numpy as np


# noinspection PyUnboundLocalVariable,PyUnboundLocalVariable,PyUnresolvedReferences,PyUnresolvedReferences
class CLA:
    """
    Implementation of Critical Line Algorithm
    to find optimal portfolios (better than generic quadratic programming)
    external methods:
    - solve(), and
    - get_max_sharpe()
    - get_min_var()
    - eff_frontier()

    """
    def __init__(self, mean, covar, l_b, u_b):
        # if (mean == np.ones(mean.shape) * mean.mean()).all(): mean[-1, 0] += 1e-5
        self.mean = mean
        self.covar = covar
        self.l_b = l_b
        self.u_b = u_b
        self.w = []  # solutions
        self.l = []  # lambdas
        self.g = []  # gammas
        self.f = []  # free weights

    def solve(self):
        # Compute the turning points,free sets and weights
        f, w = self._init_algo()
        self.w.append(np.copy(w))  # store solution
        self.l.append(None)
        self.g.append(None)
        self.f.append(f[:])
        while True:
            # 1) case a): Bound one free weight
            l_in = None
            if len(f) > 1:
                covar_f, covar_fb, mean_f, w_b = self._get_matrices(f)
                covar_f_inv = np.linalg.inv(covar_f)
                j = 0
                for i in f:
                    l, bi = self._compute_lambda(covar_f_inv, covar_fb, mean_f, w_b, j, [self.l_b[i], self.u_b[i]])
                    if l > l_in:
                        l_in, i_in, bi_in = l, i, bi
                    j += 1
            # 2) case b): Free one bounded weight
            l_out = None
            if len(f) < self.mean.shape[0]:
                b = self._get_b(f)
                for i in b:
                    covar_f, covar_fb, mean_f, w_b = self._get_matrices(f + [i])
                    covar_f_inv = np.linalg.inv(covar_f)
                    l, bi = self._compute_lambda(covar_f_inv, covar_fb, mean_f, w_b, mean_f.shape[0] - 1, self.w[-1][i])
                    if (self.l[-1] is None or l < self.l[-1]) and l > l_out:
                        l_out, i_out = l, i
            # 3) compute minimum variance solution
            if (l_in is None or l_in < 0) and (l_out is None or l_out < 0):
                self.l.append(0)
                covar_f, covar_fb, mean_f, w_b = self._get_matrices(f)
                covar_f_inv = np.linalg.inv(covar_f)
                mean_f = np.zeros(mean_f.shape)
            else:  # 4) decide lambda
                if l_in > l_out:
                    self.l.append(l_in)
                    f.remove(i_in)
                    w[i_in] = bi_in  # set value at the correct boundary
                else:
                    self.l.append(l_out)
                    f.append(i_out)
                covar_f, covar_fb, mean_f, w_b = self._get_matrices(f)
                covar_f_inv = np.linalg.inv(covar_f)
            # 5) compute solution vector
            w_f, g = self._compute_w(covar_f_inv, covar_fb, mean_f, w_b)
            for i in range(len(f)):
                w[f[i]] = w_f[i]
            self.w.append(np.copy(w))  # store solution
            self.g.append(g)
            self.f.append(f[:])
            if self.l[-1] is 0:
                break
        # 6) Purge turning points
        self._purge_num_err(10e-10)
        self._purge_excess()

    def _init_algo(self):
        # Initialize the algo
        # 1) Form structured array
        _dim = self.mean.shape[0]
        _ndtype = np.dtype([('id', int), ('mu', float)])
        a = np.zeros(_dim, dtype=_ndtype)
        b = [self.mean[i][0] for i in range(self.mean.shape[0])]  # dump array into list
        a[:] = zip(range(self.mean.shape[0]), b)
        # 2) Sort structured array
        b = np.sort(a, order='mu')
        # 3) First free weight
        i, w = b.shape[0], np.copy(self.l_b)
        while sum(w) < 1:
            i -= 1
            w[b[i][0]] = self.u_b[b[i][0]]
        w[b[i][0]] += 1 - sum(w)
        return [b[i][0]], w

    @staticmethod
    def _compute_bi(c, bi):
        if c > 0:
            bi = bi[1][0]
        if c < 0:
            bi = bi[0][0]
        return bi

    def _compute_w(self, covar_f_inv, covar_fb, mean_f, w_b):
        # 1) compute gamma
        ones_f = np.ones(mean_f.shape)
        g1 = np.dot(np.dot(ones_f.T, covar_f_inv), mean_f)
        g2 = np.dot(np.dot(ones_f.T, covar_f_inv), ones_f)
        if w_b is None:
            g, w1 = float(-self.l[-1] * g1 / g2 + 1 / g2), 0
        else:
            ones_b = np.ones(w_b.shape)
            g3 = np.dot(ones_b.T, w_b)
            g4 = np.dot(covar_f_inv, covar_fb)
            w1 = np.dot(g4, w_b)
            g4 = np.dot(ones_f.T, w1)
            g = float(-self.l[-1] * g1 / g2 + (1 - g3 + g4) / g2)
        # 2) compute weights
        w2 = np.dot(covar_f_inv, ones_f)
        w3 = np.dot(covar_f_inv, mean_f)
        return -w1 + g * w2 + self.l[-1] * w3, g

    def _compute_lambda(self, covar_f_inv, covar_fb, mean_f, w_b, i, bi):
        # 1 ) C
        ones_f = np.ones(mean_f.shape)
        c1 = np.dot(np.dot(ones_f.T, covar_f_inv), ones_f)
        c2 = np.dot(covar_f_inv, mean_f)
        c3 = np.dot(np.dot(ones_f.T, covar_f_inv), mean_f)
        c4 = np.dot(covar_f_inv, ones_f)
        c = -c1 * c2[i] + c3 * c4[i]
        if c is 0:
            return
        # 2) bi
        if type(bi) is list:
            bi = self._compute_bi(c, bi)
        # 3) Lambda
        if w_b is None:
            # All free assets
            return float((c4[i] - c1 * bi) / c), bi
        else:
            ones_b = np.ones(w_b.shape)
            l1 = np.dot(ones_b.T, w_b)
            l2 = np.dot(covar_f_inv, covar_fb)
            l3 = np.dot(l2, w_b)
            l2 = np.dot(ones_f.T, l3)
            return float(((1 - l1 + l2) * c4[i] - c1 * (bi + l3[i])) / c), bi

    def _get_matrices(self, f):
        # Slice covar_f,covar_f_b,covarB,mean_f,meanB,wF,w_b
        covar_f = self._reduce_matrix(self.covar, f, f)
        mean_f = self._reduce_matrix(self.mean, f, [0])
        b = self._get_b(f)
        covar_f_b = self._reduce_matrix(self.covar, f, b)
        w_b = self._reduce_matrix(self.w[-1], b, [0])
        return covar_f, covar_f_b, mean_f, w_b

    def _get_b(self, f):
        return list(set(range(self.mean.shape[0])) - set(f))

    @staticmethod
    def _reduce_matrix(matrix, list_x, list_y):
        # Reduce a matrix to the provided list of rows and columns
        if len(list_x) is 0 or len(list_y) is 0:
            return
        matrix_ = matrix[:, list_y[0]:list_y[0] + 1]
        for i in list_y[1:]:
            a = matrix[:, i:i + 1]
            matrix_ = np.append(matrix_, a, 1)
        matrix__ = matrix_[list_x[0]:list_x[0] + 1, :]
        for i in list_x[1:]:
            a = matrix_[i:i + 1, :]
            matrix__ = np.append(matrix__, a, 0)
        return matrix__

    def _purge_num_err(self, tol):
        # Purge violations of inequality constraints (associated with ill-conditioned covar matrix)
        i = 0
        while True:
            if i == len(self.w):
                break
            w = self.w[i]
            for j in range(w.shape[0]):
                if w[j] - self.l_b[j] < -tol or w[j] - self.u_b[j] > tol:
                    del self.w[i]
                    del self.l[i]
                    del self.g[i]
                    del self.f[i]
                    break
            i += 1

    def _purge_excess(self):
        # Remove violations of the convex hull
        i, repeat = 0, False
        while True:
            if repeat is False:
                i += 1
            if i == len(self.w) - 1:
                break
            w = self.w[i]
            mu = np.dot(w.T, self.mean)[0, 0]
            j, repeat = i + 1, False
            while True:
                if j == len(self.w):
                    break
                w = self.w[j]
                mu_ = np.dot(w.T, self.mean)[0, 0]
                if mu < mu_:
                    del self.w[i]
                    del self.l[i]
                    del self.g[i]
                    del self.f[i]
                    repeat = True
                    break
                else:
                    j += 1

    # exposed method
    def get_min_var(self):
        # Get the minimum variance solution
        var = []
        for w in self.w:
            a = np.dot(np.dot(w.T, self.covar), w)
            var.append(a)
        return min(var) ** .5, self.w[var.index(min(var))]

    # exposed method
    def get_max_sharpe(self):
        # Get the max Sharpe ratio portfolio
        # 1) Compute the local max SR portfolio between any two neighbor turning points
        w_sr, sr = [], []
        for i in range(len(self.w) - 1):
            w0 = np.copy(self.w[i])
            w1 = np.copy(self.w[i + 1])
            kargs = {'minimum': False, 'args': (w0, w1)}
            a, b = self._golden_section(self._eval_sharpe, 0, 1, **kargs)
            w_sr.append(a * w0 + (1 - a) * w1)
            sr.append(b)
        return max(sr), w_sr[sr.index(max(sr))]

    def _eval_sharpe(self, a, w0, w1):
        # Evaluate SR of the portfolio within the convex combination
        w = a * w0 + (1 - a) * w1
        # noinspection PyUnresolvedReferences
        b = np.dot(w.T, self.mean)[0, 0]
        c = np.dot(np.dot(w.T, self.covar), w)[0, 0] ** .5
        return b / c

    @staticmethod
    def _golden_section(obj, a, b, **kargs):
        # Golden section method. Maximum if kargs['minimum']==False is passed
        from math import log, ceil
        tol, sign, args = 1.0e-9, 1, None
        if 'minimum' in kargs and kargs['minimum'] is False:
            sign = -1
        if 'args' in kargs:
            args = kargs['args']
        num_iter = int(ceil(-2.078087 * log(tol / abs(b - a))))
        r = 0.618033989
        c = 1.0 - r
        # Initialize
        x1 = r * a + c * b
        x2 = c * a + r * b
        f1 = sign * obj(x1, *args)
        f2 = sign * obj(x2, *args)
        # Loop
        for _ in range(num_iter):
            if f1 > f2:
                a = x1
                x1 = x2
                f1 = f2
                x2 = c * a + r * b
                f2 = sign * obj(x2, *args)
            else:
                b = x2
                x2 = x1
                f2 = f1
                x1 = r * a + c * b
                f1 = sign * obj(x1, *args)
        if f1 < f2:
            return x1, sign * f1
        else:
            return x2, sign * f2

    # exposed method
    def eff_frontier(self, points):
        # Get the efficient frontier
        mu, sigma, weights = [], [], []
        a = np.linspace(0, 1, points / len(self.w))[:-1]  # remove the 1, to avoid duplications
        b = range(len(self.w) - 1)
        for i in b:
            w0, w1 = self.w[i], self.w[i + 1]
            if i == b[-1]:
                a = np.linspace(0, 1, points / len(self.w))  # include the 1 in the last iteration
            for j in a:
                w = w1 * j + (1 - j) * w0
                weights.append(np.copy(w))
                mu.append(np.dot(w.T, self.mean)[0, 0])
                sigma.append(np.dot(np.dot(w.T, self.covar), w)[0, 0] ** .5)
        return mu, sigma, weights
