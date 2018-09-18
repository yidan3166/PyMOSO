"""The base command."""
import os
import pathlib
import time
import collections
from datetime import date
from math import ceil
from .. import chnutils as mprun
from .. import solvers
from .. import problems
from .. import prng
from .. import testers
from json import dump


def jsonset(o):
    if isinstance(o, set):
        return list(o)
    return o.__dict__


def check_expname(name):
    if not os.path.isdir(name):
        return False
    fn = name + '/' + name + '.txt'
    fpath = pathlib.Path(fn)
    if not fpath.is_file():
        return False
    with open(fn, 'r') as f1:
        datstr = json.load(f1)
    return datstr


def get_x0(orc, xprn):
    orc0 = orc(xprn)
    feas = orc0.get_feasspace()
    startd = dict()
    endd = dict()
    for dim in feas:
        sta = []
        end = []
        for interval in feas[dim]:
            sta.append(interval[0])
            end.append(interval[1])
        startd[dim] = min(sta)
        endd[dim] = max(end)
    x0 = []
    for dim in range(orc0.dim):
        xq = xprn.sample(range(startd[dim], endd[dim]), 1)[0]
        x0.append(xq)
    x0 = tuple(x0)
    return x0


def gen_humanfile(name, probn, solvn, budget, runtime, param, vals, startseed, endseed):
    today = date.today()
    tstr = today.strftime("%A %d. %B %Y")
    timestr = time.strftime('%X')
    dnames = ('Name', 'Problem', 'Algorithm', 'Budget', 'Run time', 'Day', 'Time', 'Params', 'Param Values', 'start seed', 'end seed')
    ddate = (name, probn, solvn, budget, runtime, tstr, timestr, param, vals, startseed, endseed)
    ddict = collections.OrderedDict(zip(dnames, ddate))
    return ddict


def save_files(name, humantxt, rundat):
    mydir = name
    pathlib.Path(name).mkdir(exist_ok=True)
    humfilen = name + '.txt'
    pref = 'rundata_'
    rundatn = pref + name + '.txt'
    humpth = os.path.join(name, humfilen)
    with open(humpth, 'w') as f1:
        dump(humantxt, f1, indent=4, separators=(',', ': '))
    rundpth = os.path.join(name, rundatn)
    with open(rundpth, 'w') as f2:
        f2.write(rundat)


class BaseComm(object):
    """A base command."""

    def __init__(self, options, *args, **kwargs):
        self.options = options
        self.args = args
        self.kwargs = kwargs

    def run(self):
        raise NotImplementedError('You must implement the run() method yourself!')