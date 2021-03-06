VERBOSE=3
TITLE="checkers2d_INV"
WORKFLOW='inversion'    # inversion, migration
SOLVER='specfem2d'      # specfem2d, specfem3d
#SYSTEM='serial'       # serial, pbs, slurm
#SYSTEM='multicore'       # serial, pbs, slurm
SYSTEM='slurm_sm'       # serial, pbs, slurm
OPTIMIZE='LBFGS'        # base, newton
PREPROCESS='base'       # base
POSTPROCESS='base'      # base

MISFIT='Waveform'
#MATERIALS='LegacyAcoustic'
MATERIALS='Acoustic'
#MATERIALS='Elastic'
DENSITY='Constant'


# WORKFLOW
BEGIN=1                 # first iteration
END=100                   # last iteration
NREC=10                # number of receivers
#NREC=132                # number of receivers
#NSRC=25                 # number of sources
NSRC=1                 # number of sources
SAVEGRADIENT=1          # save gradient how often
#SAVETRACES=1


# PREPROCESSING
FORMAT='su'             # data file format
READER='su_specfem2d'
#acoustic should be z or p
CHANNELS='p'            # data channels
#try below for elastic
#CHANNELS='y'            # data channels
#CHANNELS='xz'            # data channels
NORMALIZE=0             # normalize
BANDPASS=0              # bandpass
FREQLO=0.               # low frequency corner
FREQHI=0.               # high frequency corner


# POSTPROCESSING
SMOOTH=20.              # smoothing radius
SCALE=6.0e6             # scaling factor


# OPTIMIZATION
#PRECOND=None            # preconditioner type
#STEPMAX=10              # maximum trial steps
STEPCOUNTMAX=10              # maximum trial steps
STEPTHRESH=0.1          # step length safeguard
FLIP_SIGN="yes"         # Change sign of gradient to achieve convergence


# SOLVER
NT=4800                 # number of time steps
DT=0.06                 # time step
#NT=48000                 # number of time steps
#DT=0.006                 # time step
F0=0.084                # dominant frequency


# SYSTEM
NTASK=NSRC                # must satisfy 1 <= NTASK <= NSRC
#NTASK=1                # must satisfy 1 <= NTASK <= NSRC
NPROC=1                 # processors per task
#NPROCMAX=12             # Max processes per node (? -TEC)
WALLTIME=500            # walltime

#MPIEXEC='mpirun'
#SLURMARGS='--ntasks-per-core=1'
