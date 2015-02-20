
import numpy as np

from seisflows.tools import unix
from seisflows.tools.array import loadnpy, savenpy
from seisflows.tools.code import exists
from seisflows.tools.config import ParameterObj, ParameterError

PAR = ParameterObj('SeisflowsParameters')
PATH = ParameterObj('SeisflowsPaths')

import system
import solver


class base(object):
    """ Postprocessing class

      Combines contributions from individual sources to obtain the gradient
      direction, and performs scaling, clipping, smoothing, and preconditioning
      operations on gradient in accordance with parameter settings.
    """

    def check(self):
        """ Checks parameters and paths
        """
        # check postprocessing settings
        if 'SCALE' not in PAR:
            setattr(PAR, 'SCALE', False)

        if 'CLIP' not in PAR:
            setattr(PAR, 'CLIP', 0.)

        if 'SMOOTH' not in PAR:
            setattr(PAR, 'SMOOTH', 0.)

        if 'PRECOND' not in PATH:
            setattr(PATH, 'PRECOND', None)


    def setup(self):
        """ Performs any required initialization or setup tasks
        """
        pass


    def write_gradient(self, path):
        """ Writes gradient of objective function
        """
        if 'OPTIMIZE' not in PATH:
            raise ParameterError(PATH, 'OPTIMIZE')

        if not exists(path):
            raise Exception()

        self.combine_kernels(path)
        self.process_kernels(path)

        g = solver.merge(solver.load(path +'/'+ 'gradient', verbose=True))
        savenpy(PATH.OPTIMIZE +'/'+ 'g_new', g)


    def combine_kernels(self, path):
        """ Sums individual source contributions
        """
        system.run('solver', 'combine',
                   hosts='head',
                   path=path +'/'+ 'kernels')


    def process_kernels(self, path=None, tag='gradient'):
        """ Performs scaling, smoothing, and preconditioning operations
        """
        assert (exists(path))

        # convert from relative to absolute perturbations
        g = solver.merge(solver.load(
                path +'/'+ 'kernels/sum', 
                suffix='_kernel', 
                verbose=True))

        m = solver.merge(solver.load(
                path +'/'+ 'model'))

        g *= m

        # apply scaling
        if float(PAR.SCALE) == 1.:
            pass
        elif not PAR.SCALE:
            pass
        else:
            g *= PAR.SCALE

        solver.save(path +'/'+ tag, solver.split(g))

        # apply clipping
        if PAR.CLIP > 0.:
            system.run('solver', 'clip',
                       hosts='head',
                       path=path + '/' + tag,
                       thresh=PAR.CLIP)

        # apply smoothing
        if PAR.SMOOTH > 0.:
            system.run('solver', 'smooth',
                       hosts='head',
                       path=path + '/' + tag,
                       span=PAR.SMOOTH)

            g = solver.merge(solver.load(path +'/'+ tag))

        # apply preconditioner
        if PATH.PRECOND:
            unix.cd(path)
            g /= solver.merge(solver.load(PATH.PRECOND))
            unix.mv(tag, '_noprecond')
            solver.save(path +'/'+ tag, solver.split(g))

