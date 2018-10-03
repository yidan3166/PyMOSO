"""The solve and testsolve command"""

from .basecomm import *
from inspect import getmembers, isclass
import sys
import os
import importlib.util
import importlib
from ..chnutils import testsolve, par_diff, gen_qdata, par_runs


class TestSolve(BaseComm):
    """Test a MOSO algorithm against a problem with a known solution."""
    def run(self):
        ## get the options with default values
        budget = int(self.options['--budget'])
        name = self.options['--odir']
        hasseed = self.options['--seed']
        if hasseed:
            seed = tuple(int(i) for i in self.options['<s>'])
        else:
            seed = (12345, 12345, 12345, 12345, 12345, 12345)
        isp = int(self.options['--isp'])
        proc = int(self.options['--proc'])
        radius = float(self.options['--radius'])
        x0 = tuple(int(i) for i in self.options['<x>'])
        ## determine the solver and problem
        solvarg = self.options['<solver>']
        if solvarg.endswith('.py'):
            base_mod_name = os.path.basename(solvarg).replace('.py', '')
            mod_name = '.'.join(['pydovs', 'solvers', base_mod_name])
            spec = importlib.util.spec_from_file_location(mod_name, solvarg)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            sys.modules[mod_name] = module
            smodule = importlib.import_module(mod_name)
            solvclasses = getmembers(smodule, isclass)
            solvclass = [sol[1] for sol in solvclasses if sol[0].lower() == base_mod_name][0]
        else:
            solvclasses = getmembers(solvers, isclass)
            solvclass = [sol[1] for sol in solvclasses if sol[0] == solvarg][0]
        testarg = self.options['<tester>']
        if testarg.endswith('.py'):
            mod_name = os.path.basename(testarg).replace('.py', '')
            spec = importlib.util.spec_from_file_location(mod_name, testarg)
            tmodule = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(tmodule)
            sys.modules[mod_name] = tmodule
            tmodule = importlib.import_module(mod_name)
            testclasses = getmembers(tmodule, isclass)
            testclass = [tc[1] for tc in testclasses if tc[0].lower() == mod_name][0]
        else:
            testclasses = getmembers(testers, isclass)
            testclass = [tc[1] for tc in testclasses if tc[0] == testarg][0]
        # from smodule import solvclass.__name__
        # from tmodule import testclass.__name__
        ## get the optional parameter names and values if specified
        params = self.options['<param>']
        vals = self.options['<val>']
        solve_kwargs = dict()
        solve_kwargs['budget'] = budget
        solve_kwargs['seed'] = seed
        solve_kwargs['radius'] = radius
        solve_kwargs['isp'] = isp
        solve_kwargs['proc'] = proc
        for i, p in enumerate(params):
            solve_kwargs[p] = float(vals[i])
        start_opt_time = time.time()
        print('** Testing ', solvarg, ' using ', testarg, ' **')
        stsstr = '-- using starting seed:'
        print(f'{stsstr:26} {seed[0]:12} {seed[1]:12} {seed[2]:12} {seed[3]:12} {seed[4]:12} {seed[5]:12}')
        res, end_seed = testsolve(testclass, solvclass, x0, **solve_kwargs)
        end_opt_time = time.time()
        opt_durr = end_opt_time - start_opt_time
        humtxt = gen_humanfile(name, testarg, solvarg, budget, opt_durr, params, vals, seed, end_seed)
        seed = tuple([int(i) for i in end_seed])
        endstr = '-- ending seed:'
        print(f'{endstr:26} {seed[0]:12} {seed[1]:12} {seed[2]:12} {seed[3]:12} {seed[4]:12} {seed[5]:12}')
        print('-- Optimization run time: {0:.2f} seconds'.format(opt_durr))
        reslst = []
        for r in res:
            reslst.append(str(res[r]))
        resstr = '\n'.join(reslst)
        save_files(name, humtxt, resstr)
        print('-- Done!')
