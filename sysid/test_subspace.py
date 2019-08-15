"""
Unit testing.
"""
import unittest
import pylab as pl
import sysid
import sysid.subspace

pl.ion()

# pylint: disable=invalid-name, no-self-use

ENABLE_PLOTTING = False


class TestSubspace(unittest.TestCase):
    """
    Unit testing.
    """

    def test_block_hankel(self):
        """
        Block hankel function.
        """
        y = pl.rand(3, 100)
        Y = sysid.subspace.block_hankel(y, 5)
        self.assertEqual(Y.shape, (15, 95))

    def test_subspace_det_algo1_siso(self):
        """
        Subspace deterministic algorithm (SISO).
        """
        ss1 = sysid.StateSpaceDiscreteLinear(
            A=0.9, B=0.5, C=1, D=0, Q=0.01, R=0.01, dt=0.1)

        pl.seed(1234)
        prbs1 = sysid.prbs(1000)

        def f_prbs(t, x, i):
            "input function"
            # pylint: disable=unused-argument, unused-variable
            return prbs1[i]

        tf = 10
        data = ss1.simulate(f_u=f_prbs, x0=pl.matrix(0), tf=tf)
        ss1_id = sysid.subspace_det_algo1(
            y=data.y, u=data.u,
            f=5, p=5, s_tol=1e-1, dt=ss1.dt)
        data_id = ss1_id.simulate(f_u=f_prbs, x0=0, tf=tf)
        nrms = sysid.subspace.nrms(data_id.y, data.y)
        self.assertGreater(nrms, 0.9)

        if ENABLE_PLOTTING:
            pl.plot(data_id.t.T, data_id.x.T, label='id')
            pl.plot(data.t.T, data.x.T, label='true')
            pl.legend()
            pl.grid()

    def test_subspace_det_algo1_mimo(self):
        """
        Subspace deterministic algorithm (MIMO).
        """
        ss2 = sysid.StateSpaceDiscreteLinear(
            A=pl.matrix([[0, 0.1, 0.2],
                         [0.2, 0.3, 0.4],
                         [0.4, 0.3, 0.2]]),
            B=pl.matrix([[1, 0],
                         [0, 1],
                         [0, -1]]),
            C=pl.matrix([[1, 0, 0],
                         [0, 1, 0]]),
            D=pl.matrix([[0, 0],
                         [0, 0]]),
            Q=pl.diag([0.01, 0.01, 0.01]), R=pl.diag([0.01, 0.01]), dt=0.1)
        pl.seed(1234)
        prbs1 = sysid.prbs(1000)
        prbs2 = sysid.prbs(1000)

        def f_prbs_2d(t, x, i):
            "input function"
            #pylint: disable=unused-argument
            i = i % 1000
            return 2*pl.matrix([prbs1[i]-0.5, prbs2[i]-0.5]).T
        tf = 8
        data = ss2.simulate(
            f_u=f_prbs_2d, x0=pl.matrix([0, 0, 0]).T, tf=tf)
        ss2_id = sysid.subspace_det_algo1(
            y=data.y, u=data.u,
            f=5, p=5, s_tol=0.1, dt=ss2.dt)
        data_id = ss2_id.simulate(
            f_u=f_prbs_2d,
            x0=pl.matrix(pl.zeros(ss2_id.A.shape[0])).T, tf=tf)
        nrms = sysid.nrms(data_id.y, data.y)
        self.assertGreater(nrms, 0.9)

        if ENABLE_PLOTTING:
            for i in range(2):
                pl.figure()
                pl.plot(data_id.t.T, data_id.y[i, :].T,
                        label='$y_{:d}$ true'.format(i))
                pl.plot(data.t.T, data.y[i, :].T,
                        label='$y_{:d}$ id'.format(i))
                pl.legend()
                pl.grid()


if __name__ == "__main__":
    unittest.main()

# vim: set et ft=python fenc=utf-8 ff=unix sts=4 sw=4 ts=4 :
