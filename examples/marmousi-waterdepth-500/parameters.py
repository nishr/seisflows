VERBOSE=0
TITLE='marmousi-test'
WORKFLOW='inversion' # inversion, migration, modeling
SOLVER='specfem2d'   # specfem2d, specfem3d
#SYSTEM='serial'    # serial, pbs, slurm
SYSTEM='multicore'    # serial, pbs, slurm
OPTIMIZE='LBFGS'     # base
PREPROCESS='base'    # base
POSTPROCESS='base'   # base

MISFIT='Waveform'
MATERIALS='Acoustic'
DENSITY='Constant'

# WORKFLOW
BEGIN=1                 # first iteration
END=10                  # last iteration
NREC=500                # number of receivers
NREC=50                # number of receivers
NSRC=32                 # number of sources
#NSRC=1                 # number of sources
SAVEGRADIENT=1          # save gradient how often


# PREPROCESSING
FORMAT='su'
READER='su_specfem2d'   # data file format
#CHANNELS='xz'           # data channels
CHANNELS='p'           # data channels
NORMALIZE=0             # normalize
#NORMALIZE="NormalizeTracesL1"
BANDPASS=0              # bandpass
MUTE=0                  # mute direct arrival
FREQLO=0.               # low frequency corner
FREQHI=0.               # high frequency corner
MUTECONST=0.75          # mute constant
MUTESLOPE=1500.         # mute slope


# OPTIMIZATION
STEPMAX=10              # maximum trial steps
STEPTHRESH=0.1          # step length safeguard

# POSTPROCESSING
SMOOTH=5.               # smoothing radius
SCALE=1.                # scaling factor

# SOLVER
NT=6000                 # number of time steps
DT=1.0e-3               # time step
F0=5.0                  # dominant frequency

# SYSTEM
NTASK=NSRC              # number of tasks
NPROC=1                 # processors per task
WALLTIME=500            # walltime

