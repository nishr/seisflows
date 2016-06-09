
import subprocess
from glob import glob
from os.path import join

import numpy as np

import seisflows.seistools.specfem3d_globe as solvertools
from seisflows.seistools.shared import getpar, setpar, Model, Minmax
from seisflows.seistools.io import loadbypar, copybin, loadbin, savebin

from seisflows.tools import unix
from seisflows.tools.array import loadnpy, savenpy
from seisflows.tools.code import Struct, exists, mpicall
from seisflows.tools.config import SeisflowsParameters, SeisflowsPaths, \
    ParameterError, custom_import

PAR = SeisflowsParameters()
PATH = SeisflowsPaths()

import system


class specfem3d_globe(custom_import('solver', 'base')):
    """ Python interface for SPECFEM3D_GLOBE

      See base class for method descriptions
    """

    if PAR.MATERIALS in ['Isotropic']:
        parameters = []
        parameters += ['vp']
        parameters += ['vs']
    else:
        parameters = []
        parameters += ['vpv']
        parameters += ['vph']
        parameters += ['vsv']
        parameters += ['vsh']
        parameters += ['eta']


    def check(self):
        """ Checks parameters and paths
        """
        super(specfem3d_globe, self).check()

        if 'CHANNELS' not in PAR:
            setattr(PAR, 'CHANNELS', 'Z')

        # check data format
        if 'FORMAT' not in PAR:
            raise Exception()


    def generate_data(self, **model_kwargs):
        """ Generates data
        """
        self.generate_mesh(**model_kwargs)

        unix.cd(self.getpath)
        setpar('SIMULATION_TYPE', '1')
        setpar('SAVE_FORWARD', '.true.')
        mpicall(system.mpiexec(), 'bin/xspecfem3D')

        if PAR.FORMAT in ['ASCII', 'ascii']:
            src = glob('OUTPUT_FILES/*.sem.ascii')
            dst = 'traces/obs'
            unix.mv(src, dst)


    def generate_mesh(self, model_path=None, model_name=None, model_type='gll'):
        """ Performs meshing and database generation
        """
        assert(model_name)
        assert(model_type)

        self.initialize_solver_directories()
        unix.cd(self.getpath)

        if model_type == 'gll':
            assert (exists(model_path))
            self.check_mesh_properties(model_path)

            unix.cp(glob(model_path +'/'+ '*'), self.model_databases)

            mpicall(system.mpiexec(), 'bin/xmeshfem3D')
            self.export_model(PATH.OUTPUT +'/'+ model_name)

        else:
            raise NotImplementedError


    ### model input/output

    def load(self, path, prefix='reg1_', suffix='', verbose=False):
        """ reads SPECFEM model or kernel

          Models are stored in Fortran binary format and separated into multiple
          files according to material parameter and processor rank.
        """
        model = Model(self.parameters)
        minmax = Minmax(self.parameters)

        for iproc in range(self.mesh_properties.nproc):
            # read database files
            keys, vals = loadbypar(path, self.parameters, iproc, prefix, suffix)
            for key, val in zip(keys, vals):
                model[key] += [val]

            minmax.update(keys, vals)

        if verbose:
            minmax.write(path, logpath=PATH.SUBMIT)

        return model


    def save(self, path, model, prefix='reg1_', suffix=''):
        """ writes SPECFEM3D_GLOBE transerverly isotropic model
        """
        unix.mkdir(path)

        for iproc in range(self.mesh_properties.nproc):
            for key in ['vpv', 'vph', 'vsv', 'vsh', 'eta']:
                if key in self.parameters:
                    savebin(model[key][iproc], path, iproc, prefix+key+suffix)
                elif 'kernel' in suffix:
                    pass
                else:
                    src = PATH.OUTPUT +'/'+ 'model_init'
                    dst = path
                    copybin(src, dst, iproc, prefix+key+suffix)

            if 'rho' in self.parameters:
                savebin(model['rho'][iproc], path, iproc, prefix+'rho'+suffix)
            elif 'kernel' in suffix:
                pass
            else:
                src = PATH.OUTPUT +'/'+ 'model_init'
                dst = path
                copybin(src, dst, iproc, prefix+'rho'+suffix)



    ### low-level solver interface

    def forward(self, path='traces/syn'):
        """ Calls SPECFEM3D_GLOBE forward solver
        """
        solvertools.setpar('SIMULATION_TYPE', '1')
        solvertools.setpar('SAVE_FORWARD', '.true.')
        mpicall(system.mpiexec(), 'bin/xspecfem3D')

        if PAR.FORMAT in ['ASCII', 'ascii']:
            src = glob('OUTPUT_FILES/*.sem.ascii')
            dst = path
            unix.mv(src, dst)


    def adjoint(self):
        """ Calls SPECFEM3D_GLOBE adjoint solver
        """
        solvertools.setpar('SIMULATION_TYPE', '3')
        solvertools.setpar('SAVE_FORWARD', '.false.')
        unix.rm('SEM')
        unix.ln('traces/adj', 'SEM')
        mpicall(system.mpiexec(), 'bin/xspecfem3D')


    def check_mesh_properties(self, path=None, parameters=None):
        if not hasattr(self, '_mesh_properties'):
            if not path:
                path = PATH.MODEL_INIT

            if not parameters:
                parameters = self.parameters

            nproc = 0
            ngll = []
            while True:
                dummy = loadbin(path, nproc, 'reg1_'+parameters[0])
                ngll += [len(dummy)]
                nproc += 1
                if not exists('%s/proc%06d_reg1_%s.bin' % (path, nproc, parameters[0])):
                    break

            self._mesh_properties = Struct([
                ['nproc', nproc],
                ['ngll', ngll]])

        return self._mesh_properties


    def rename_data(self):
        """ Works around conflicting data filename conventions
        """
        files = glob(self.getpath +'/'+ 'traces/adj/*sem.ascii')
        unix.rename('sem.ascii', 'sem.ascii.adj', files)


    def initialize_adjoint_traces(self):
        super(specfem3d_globe, self).initialize_adjoint_traces()

        # hack to deal with SPECFEM2D's use of different name conventions for
        # regular traces and 'adjoint' traces
        if PAR.FORMAT in ['SU', 'su']:
            files = glob(self.getpath +'/'+ 'traces/adj/*SU')
            unix.rename('_SU', '_SU.adj', files)

        # hack to deal with SPECFEM3D's requirement that all components exist,
        # even ones not in use
        unix.cd(self.getpath +'/'+ 'traces/adj')
        for iproc in range(PAR.NPROC):
            for channel in ['x', 'y', 'z']:
                src = '%d_d%s_SU.adj' % (iproc, PAR.CHANNELS[0])
                dst = '%d_d%s_SU.adj' % (iproc, channel)
                if not exists(dst):
                    unix.cp(src, dst)


    @property
    def data_filenames(self):
        unix.cd(self.getpath)
        unix.cd('traces/obs')

        print 'made it here'
        if PAR.FORMAT in ['ASCII', 'ascii']:
            filenames = []
            for channel in PAR.CHANNELS:
                filenames += glob('*.??%s.sem.ascii' % channel)
            return [filenames]

    @property
    def kernel_databases(self):
        return join(self.getpath, 'OUTPUT_FILES/DATABASES_MPI')

    @property
    def model_databases(self):
        return join(self.getpath, 'OUTPUT_FILES/DATABASES_MPI')

    @property
    def source_prefix(self):
        return 'CMTSOLUTION'


