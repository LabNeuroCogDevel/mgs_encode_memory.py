#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on February 2016
@author: Luca Filippin - luca.filippin@gmail.com

Utility to execute python module under PsychoPy python environment.

use like :
  ~/mgs_encode_memory.py/PsychoPyPython.py -r /Applications/PsychoPy2.app -s -p -a ~/mgs_encode_memory.py/mgs_recall.py 
'''

import subprocess
import locale
import argparse
import traceback
import codecs
import sys
import os

_NAME = 'PsychoPy Python' 
_DATE = 'Feb 2016'
_VERSION = '1.0.0'

_PATH_PREPEND  = 'pb'
_PATH_POSTPEND = 'pe'
_PATH_SET      = 'ps'
_PATH_NOT      = 'pn'

def parserOptions(args = sys.argv[1:]):
    desc = '%s: run any cmd within PsychoPy environment (%s)' %(_NAME, _DATE)

    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('--version', action = 'version', version = '%(prog)s ' + 'v%s' %_VERSION)
    parser.add_argument('-v', "--verbose", dest = "verbose", action="store_true", default = False, help = 'Be informative')
    parser.add_argument('-r', "--psychopy-root", dest = "psychopy_root",  default = None, help = 'PsychoPy application root directory')
    parser.add_argument('-b', "--no-bytecode", dest = "no_bytecode",  action = 'store_true', help = 'Set environment to not generate bytecode')
    parser.add_argument('-s', "--use-shell", dest = "use_shell", action = 'store_true', help = 'Run in a shell')
    parser.add_argument('-p', "--prepend-interpreter", dest = "prepend_interpreter",  action = 'store_true', help = 'Prepend python interpreter to command arguments')
    parser.add_argument('-w', "--working-dir", dest = "working_dir",  default = None, help = 'Working directory')
    helpStr = 'Set environment variable: -e <var name> <value> <{0}|{1}|{2}|{3}>. This option maybe used multiple times: {0} = path prepend, {1} = path postpend, {2} = path set, {3} = not a path'.format(_PATH_PREPEND, _PATH_POSTPEND, _PATH_SET, _PATH_NOT)
    parser.add_argument('-e', "--environment-var", dest = "env_var",  nargs = 3, action='append', default = [], help = helpStr)
    parser.add_argument('-a', "--arguments", dest = "arguments", nargs = argparse.REMAINDER, required = True, help = 'Arguments to pass to the python interpreter (all args after this option are passed through)')
    
    o = parser.parse_args() 

    if o.working_dir == None:
        o.working_dir = os.getcwd()
    if o.psychopy_root == None:
        o.psychopy_root = os.path.dirname(sys.executable)
    elif not os.path.isdir(o.psychopy_root):
        o.psychopy_root = codecs.open(o.psychopy_root, 'r', encoding='utf-8').readline().strip()
    var_env_act = (_PATH_PREPEND, _PATH_SET, _PATH_POSTPEND, _PATH_NOT)
    for var, val, act in o.env_var:
        if act not in var_env_act:
            raise ValueError('Not a valid option for environment variable. Possible choices are: %s' %str(var_env_act)) 
    return o

def setEnvVar(env, var, value, isPath = False, overWrite = False, prepend = True):
    value = unicode(value).encode(locale.getpreferredencoding())
    if overWrite or not (var in env) or not isPath:
        env[var] = value
    elif isPath:
        env[var] = os.pathsep.join((value, env[var]) if prepend else (env[var], value)) 
    return env

def setPsychoPyEnv(psychopyRoot, noByteCode, envVarVal):
    env = os.environ.copy()
    if sys.platform == 'darwin':
        setEnvVar(env, 'PYTHONPATH', os.path.join(psychopyRoot, "Contents", "Resources"), isPath = True, overWrite = True)
        setEnvVar(env, 'RESOURCEPATH', os.path.join(psychopyRoot, "Contents", "Resources"), isPath = True, overWrite = True)
        setEnvVar(env, 'PYTHONHOME', os.path.join(psychopyRoot, "Contents", "Resources"), isPath = True, overWrite = True)
        setEnvVar(env, 'MATPLOTLIBDATA', os.path.join(psychopyRoot, "Contents", "Resources", "mpl-data"), isPath = True, overWrite = True)
        setEnvVar(env, 'EXECUTABLEPATH', os.path.join(psychopyRoot, "Contents", "MacOS", "PsychoPy2"), isPath = True, overWrite = True)
        setEnvVar(env, 'ARGVZERO', os.path.join(psychopyRoot,  "Contents", "MacOS", "PsychoPy2"), isPath = True, overWrite = True)
        setEnvVar(env, 'PYTHONDONTWRITEBYTECODE', 1 if noByteCode else 0, isPath = False, overWrite = True)
        pythonExe = os.path.join(psychopyRoot, 'Contents', 'MacOS', 'python')
    elif sys.platform == 'win32':
        pythonExe = os.path.join(psychopyRoot, 'python')
    else:
        raise RuntimeError('Platform not supported: %s' %sys.platform)
    for var, val, act in envVarVal:
        setEnvVar(env, var, val, isPath = act in (_PATH_PREPEND, _PATH_POSTPEND, _PATH_SET), overWrite = act in (_PATH_SET, _PATH_NOT), prepend = act == _PATH_PREPEND)
    return pythonExe, env

def run(psychopyRoot, prependInterpreter, noByteCode, workingDir, envVarVal, useShell, argsList):
    pythonExe, env = setPsychoPyEnv(psychopyRoot, noByteCode, envVarVal)
    argsList = [ pythonExe ] + argsList if prependInterpreter else argsList
    print(argsList)
    p = subprocess.Popen(argsList, cwd = workingDir, env = env)
    p.wait()
    rc = p.returncode
    return rc
    
if __name__ == '__main__':
    exitCode = 0
    try:
        o = parserOptions()
        exitCode = run(o.psychopy_root, o.prepend_interpreter, o.no_bytecode, o.working_dir, o.env_var, o.use_shell, o.arguments)
    except Exception, e:
        print '--- ERROR ---'
        print traceback.print_exc()
        exitCode = 1
    sys.exit(exitCode)

