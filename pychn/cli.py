"""
pychn

Usage:
  pychn listitems
  pychn solve [--budget=B] [--name=N] [--radius=R] [(--parsim --proc=Q)]
            [(--seed <s> <s> <s> <s> <s> <s>)] [(--params <param> <val>)]...
            <problem> <solver> <x>...
  pychn -h | --help
  pychn -v | --version

Options:
  --budget=B                Simulation budget [default: 50000]
  --x0                      Specify a feasible point as spaced integers.
  --isp=T                   Number of independent sample paths of the algorithm to solve. [default: 1]
  --name=N                  A name to assign to the output. [default: testrun]
  --seed                    Specify a seed by entering 6 spaced integers > 0.
  --radius=R                Specify a neighborhood radius. [default: 1]
  --parsim                  Run simulations in parallel if proc is specified. [default: 1]
  --proc=Q                  Total number of processes to make available to pychn. [default: 1]
  --params                  Allows specifying param val pairs.
  -h --help                 Show this screen.
  -v --version              Show version.

Examples:
  pychn solve ProbTPA RPERLE 4 14
  pychn solve --budget=100000 --name=test1 --radius=3 ProbTPB RMINRLE 3 12
  pychn solve --seed 12345 32123 5322 2 9543 666666666 ProbTPC RPERLE 31 21 11
  pychn solve --parsim --proc=4 --params betaeps 0.4 ProbTPA RPERLE 30 30
  pychn solve --params betaeps 0.7 --params betadel 0.5 ProbTPA RPERLE 45 45

Help:
  Use the listitems command to view a list of available solvers, problems, and
  test problems.

  Use solve to generate a solution to <problem> using algorithm <solver>.
  After specifying any desired options, optionally specify algorithm-specific
  parameters and their values. For complex, long-running simulations, specify
  the --mp option to take replications in parallel.

  Use testsolve to generate a solution to a <tester> test problem using
  algorithm <solver>. The listitems command shows which problems have an
  associated tester and how to specify the tester. Testers are problems for
  which a solution is known and implemented. In addition to the regular run
  data, testsolve will generate solution quality metrics against the known
  solution. Testsolve can run independent instances of the chosen algorithm
  by setting the --isp option. The user may specify both --trails and --mp
  but should choose values carefully if doing so.

  An experiment is any single invocation of solve or testsolve. Experiments can
  be instances of an algorithm run in parallel using independent random numbers
  by setting the --isp option. The simulation budget determines how many
  simulation replications an algorithm instance uses to generate a solution, and
  can be set using --budget. Use --name to assign a name to the experiment. A
  directory will be generated with the given name in the working directory. Make
  sure the user invoking pychn has write access to the working directory. The
  -seed option specifies 6 positive integers used to generate random number
  streams used in the experiment. The neighborhood radius specifies the maximum
  distance between feasible points such that an compliant algorithm considers
  them neighbors. Since algorithms in pychn are integer-ordered, --nr values
  less than 1 are trivial. Finally, simulation replications can be taken in
  parallel for simulations with non-trival run times using --mp. When using
  --isp and --mp, (or both) choose values appropriate for the machine, as
  pychn will not adjust them.
"""


from inspect import getmembers, isclass

from docopt import docopt

from . import __version__ as VERSION


def main():
    """Main CLI entrypoint."""
    import pychn.commands
    options = docopt(__doc__, version=VERSION)
    for (k, v) in options.items():
        if hasattr(pychn.commands, k) and v:
            commod = getattr(pychn.commands, k)
            comclasses = getmembers(commod, isclass)
            comclass = [cmcls[1] for cmcls in comclasses if cmcls[0] != 'BaseComm' and issubclass(cmcls[1], pychn.commands.basecomm.BaseComm)][0]
            cominst = comclass(options)
            cominst.run()
