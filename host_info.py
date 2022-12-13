import re
import socket
import sys


class Hosts:
    """
    object to contain host info
    """
    def __init__(self, tasktype, name=None, pp_address=None, ET=None):
        self.tasktype = tasktype
        self.name = name if name else (tasktype + '_unknown')
        # default to pyparallel default
        # maybe could just pass None?
        if not pp_address:
            if 'linux' in sys.platform:
                pp_address = '/dev/parport0'
            else:
                pp_address = 0x0378
        self.pp_address = pp_address
        self.ET = ET

    def __str__(self):
        return self.tasktype


def host_tasktype():
    """ return a host object with task hostname and parallel port info """
    hostname = socket.gethostname()
    type_host_lookup = {
        'eeg': ['Oaco14Datapb1','DESKTOP-I2CP6M6'],
        'ieeg': ['abel-XPS-13-9380'],
        'mri': ['7T-EPRIME-PC',  # task
                # recall
                'MRRCNewwin7-PC', # 2022-12-12
                'mc-wifi-10-215-130-29.wireless.pitt.edu',
                'JulliesiMac.local'],
        'practice': ['eyelab130xx'],  # behave instead
        'behave': ['eyelab130', 'eprime'],  # 20180814 -- eyelab130 died!
        'test': ['reese', 'kt']}

    host_pp = {
        'eyelab130': 0x0378,
        'Oaco14Datapb1': 0xDFF8,
        'DESKTOP-I2CP6M6': 0xD010,
        'abel-XPS-13-9380': '/dev/parpart0'}

    host_eye = {
        'eyelab130': 'ASL',
        '7T-EPRIME-PC': 'arrington',
        'MRRCNewwin7-PC': 'arrington',
        'abel-XPS-13-9380': 'pylink'}

    # default to uknown task
    tasktype = 'unknown'
    if re.search('.*.wireless.pitt.edu', hostname):
        tasktype = 'mri'
    else:
        for typekey, hosts_using_type in type_host_lookup.items():
            if hostname in hosts_using_type:
                tasktype = typekey
                print("%s matches %s" % (hostname, tasktype))

    if tasktype == 'unknown':
        print("dont know about host '%s', task type is unknown" % hostname)

    return(Hosts(tasktype, hostname,
                 host_pp.get(hostname),
                 host_eye.get(hostname)))
