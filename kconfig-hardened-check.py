#!/usr/bin/python3

#
# This script helps me to check the Linux kernel Kconfig option list
# against my hardening preferences for x86_64. Let the computers do their job!
#
# Author: Alexander Popov <alex.popov@linux.com>
#
# Please don't cry if my Python code looks like C.
#

# N.B Hardening command line parameters:
#    page_poison=1
#    slub_debug=P
#    slab_nomerge
#    pti=on
#    kernel.kptr_restrict=1

import sys, getopt
from collections import namedtuple
import re

debug_mode = False  # set it to True to print the unknown options from the config
error_count = 0
opt_list = []

Opt = namedtuple('Opt', ['name', 'state', 'decision', 'reason'])

def construct_opt_list():
    opt_list.append([Opt('FORTIFY_SOURCE',          'y', 'ubuntu18', 'self_protection'), ''])
    opt_list.append([Opt('SLAB_FREELIST_HARDENED',  'y', 'ubuntu18', 'self_protection'), ''])
    opt_list.append([Opt('PAGE_TABLE_ISOLATION',    'y', 'ubuntu18', 'self_protection'), ''])
    opt_list.append([Opt('SLAB_FREELIST_RANDOM',    'y', 'ubuntu18', 'self_protection'), ''])
    opt_list.append([Opt('RANDOMIZE_BASE',          'y', 'ubuntu18', 'self_protection'), ''])
    opt_list.append([Opt('STRICT_KERNEL_RWX',       'y', 'ubuntu18', 'self_protection'), ''])
    opt_list.append([Opt('STRICT_MODULE_RWX',       'y', 'ubuntu18', 'self_protection'), ''])
    opt_list.append([Opt('DEBUG_WX',                'y', 'ubuntu18', 'self_protection'), ''])
    opt_list.append([Opt('STRICT_DEVMEM',           'y', 'ubuntu18', 'self_protection'), ''])
    opt_list.append([Opt('RETPOLINE',               'y', 'ubuntu18', 'self_protection'), ''])
    opt_list.append([Opt('HARDENED_USERCOPY',       'y', 'ubuntu18', 'self_protection'), ''])
    opt_list.append([Opt('VMAP_STACK',              'y', 'ubuntu18', 'self_protection'), ''])
    opt_list.append([Opt('THREAD_INFO_IN_TASK',     'y', 'ubuntu18', 'self_protection'), ''])
    opt_list.append([Opt('RANDOMIZE_BASE',          'y', 'ubuntu18', 'self_protection'), ''])
    opt_list.append([Opt('RANDOMIZE_MEMORY',        'y', 'ubuntu18', 'self_protection'), ''])
    opt_list.append([Opt('BUG',                     'y', 'ubuntu18', 'self_protection'), ''])
    opt_list.append([Opt('SYN_COOKIES',             'y', 'ubuntu18', 'self_protection'), ''])
    opt_list.append([Opt('SECCOMP',                 'y', 'ubuntu18', 'self_protection'), ''])
    opt_list.append([Opt('SECCOMP_FILTER',          'y', 'ubuntu18', 'self_protection'), ''])
    opt_list.append([Opt('SCHED_STACK_END_CHECK',   'y', 'ubuntu18', 'self_protection'), ''])
    opt_list.append([Opt('MODULE_SIG',              'y', 'ubuntu18', 'self_protection'), ''])
    opt_list.append([Opt('MODULE_SIG_ALL',          'y', 'ubuntu18', 'self_protection'), ''])
    opt_list.append([Opt('MODULE_SIG_SHA512',       'y', 'ubuntu18', 'self_protection'), ''])
    opt_list.append([Opt('SLUB_DEBUG',              'y', 'ubuntu18', 'self_protection'), ''])
    opt_list.append([Opt('CC_STACKPROTECTOR_STRONG','y', 'ubuntu18', 'self_protection'), ''])
    opt_list.append([Opt('DEFAULT_MMAP_MIN_ADDR',   '65536', 'ubuntu18', 'self_protection'), ''])

    opt_list.append([Opt('DEBUG_LIST',                       'y', 'kspp', 'self_protection'), ''])
    opt_list.append([Opt('BUG_ON_DATA_CORRUPTION',           'y', 'kspp', 'self_protection'), ''])
    opt_list.append([Opt('PAGE_POISONING',                   'y', 'kspp', 'self_protection'), ''])
    opt_list.append([Opt('GCC_PLUGINS',                      'y', 'kspp', 'self_protection'), ''])
    opt_list.append([Opt('GCC_PLUGIN_RANDSTRUCT',            'y', 'kspp', 'self_protection'), ''])
    opt_list.append([Opt('GCC_PLUGIN_STRUCTLEAK',            'y', 'kspp', 'self_protection'), ''])
    opt_list.append([Opt('GCC_PLUGIN_STRUCTLEAK_BYREF_ALL',  'y', 'kspp', 'self_protection'), ''])
    opt_list.append([Opt('GCC_PLUGIN_LATENT_ENTROPY',        'y', 'kspp', 'self_protection'), ''])
    opt_list.append([Opt('IO_STRICT_DEVMEM',                 'y', 'kspp', 'self_protection'), ''])
    opt_list.append([Opt('REFCOUNT_FULL',                    'y', 'kspp', 'self_protection'), ''])
    opt_list.append([Opt('DEBUG_SG',                         'y', 'kspp', 'self_protection'), ''])
    opt_list.append([Opt('DEBUG_CREDENTIALS',                'y', 'kspp', 'self_protection'), ''])
    opt_list.append([Opt('DEBUG_NOTIFIERS',                  'y', 'kspp', 'self_protection'), ''])
    opt_list.append([Opt('MODULE_SIG_FORCE',                 'y', 'kspp', 'self_protection'), ''])
    opt_list.append([Opt('HARDENED_USERCOPY_FALLBACK',       'is not set', 'kspp', 'self_protection'), ''])
    opt_list.append([Opt('GCC_PLUGIN_STACKLEAK',             'y', 'my', 'self_protection'), ''])
    opt_list.append([Opt('SLUB_DEBUG_ON',                    'y', 'my', 'self_protection'), ''])
    opt_list.append([Opt('SECURITY_DMESG_RESTRICT',          'y', 'my', 'self_protection'), ''])
    opt_list.append([Opt('STATIC_USERMODEHELPER',            'y', 'my', 'self_protection'), '']) # breaks systemd?

    opt_list.append([Opt('SECURITY',                    'y', 'ubuntu18', 'security_policy'), ''])
    opt_list.append([Opt('SECURITY_YAMA',               'y', 'ubuntu18', 'security_policy'), ''])
    opt_list.append([Opt('SECURITY_SELINUX_DISABLE',    'is not set', 'ubuntu18', 'security_policy'), ''])

    opt_list.append([Opt('ACPI_CUSTOM_METHOD',   'is not set', 'ubuntu18', 'cut_attack_surface'), ''])
    opt_list.append([Opt('COMPAT_BRK',           'is not set', 'ubuntu18', 'cut_attack_surface'), ''])
    opt_list.append([Opt('DEVKMEM',              'is not set', 'ubuntu18', 'cut_attack_surface'), ''])
    opt_list.append([Opt('COMPAT_VDSO',          'is not set', 'ubuntu18', 'cut_attack_surface'), ''])

    opt_list.append([Opt('LEGACY_VSYSCALL_NONE', 'y', 'kspp', 'cut_attack_surface'), '']) # 'vsyscall=none'
    opt_list.append([Opt('BINFMT_MISC',          'is not set', 'kspp', 'cut_attack_surface'), ''])
    opt_list.append([Opt('KEXEC',                'is not set', 'kspp', 'cut_attack_surface'), ''])
    opt_list.append([Opt('PROC_KCORE',           'is not set', 'kspp', 'cut_attack_surface'), ''])
    opt_list.append([Opt('LEGACY_PTYS',          'is not set', 'kspp', 'cut_attack_surface'), ''])
    opt_list.append([Opt('MODIFY_LDT_SYSCALL',   'is not set', 'kspp', 'cut_attack_surface'), ''])
    opt_list.append([Opt('KEXEC_FILE',           'is not set', 'my', 'cut_attack_surface'), ''])
    opt_list.append([Opt('LIVEPATCH',            'is not set', 'my', 'cut_attack_surface'), ''])
    opt_list.append([Opt('NAMESPACES',           'is not set', 'my', 'cut_attack_surface'), '']) # user.max_user_namespaces=0
    opt_list.append([Opt('IP_DCCP',              'is not set', 'my', 'cut_attack_surface'), ''])
    opt_list.append([Opt('FTRACE',               'is not set', 'my', 'cut_attack_surface'), ''])
    opt_list.append([Opt('KPROBES',              'is not set', 'my', 'cut_attack_surface'), ''])
    opt_list.append([Opt('PROFILING',            'is not set', 'my', 'cut_attack_surface'), ''])
    opt_list.append([Opt('UPROBES',              'is not set', 'my', 'cut_attack_surface'), ''])
    opt_list.append([Opt('BPF_JIT',              'is not set', 'my', 'cut_attack_surface'), ''])
    opt_list.append([Opt('BPF_SYSCALL',          'is not set', 'my', 'cut_attack_surface'), ''])

    opt_list.append([Opt('LKDTM',    'm', 'my', 'feature_test'), ''])


def print_opt_list():
    print('[+] Printing kernel hardening preferences...')
    print('  {:<39}|{:^13}|{:^10}|{:^20}'.format('option name', 'desired val', 'decision', 'reason'))
    print('  ======================================================================================')
    for o in opt_list:
        print('  CONFIG_{:<32}|{:^13}|{:^10}|{:^20}'.format(o[0].name, o[0].state, o[0].decision, o[0].reason))
    print()


def print_check_results():
    global error_count

    print('  {:<39}|{:^13}|{:^10}|{:^20}||{:^20}'.format('option name', 'desired val', 'decision', 'reason', 'check result'))
    print('  ===========================================================================================================')
    for o in opt_list:
        if o[1] == '':
            error_count += 1
            o[1] = 'FAIL: not found'
        print('  CONFIG_{:<32}|{:^13}|{:^10}|{:^20}||{:^20}'.format(o[0].name, o[0].state, o[0].decision, o[0].reason, o[1]))
    print()


def check_state(option):
    global error_count
    found = False

    for o in opt_list:
        if option[0] == o[0].name:
            found = True

            if o[1] != '':
                sys.exit('[!] BUG: CONFIG_{} was found more than once'.format(o[0].name))

            if option[1] == o[0].state:
                o[1] = 'OK'
            else:
                o[1] = 'FAIL: "' + option[1] + '"'
                error_count += 1

    if not found and debug_mode:
        print("DEBUG: dunno about option {} ".format(option))


def check_on(line):
    if line[:7] != 'CONFIG_':
        sys.exit('[!] BUG: bad enabled config option "{}"'.format(line))

    line_parts = line[7:].split('=')
    check_state(line_parts)


def check_off(line):
    if line[:9] != '# CONFIG_':
        sys.exit('[!] BUG: bad disabled config option "{}"'.format(line))

    line_parts = line[9:].split(' ', 1)

    if line_parts[1] != 'is not set':
        sys.exit('[!] BUG: bad disabled config option "{}"'.format(line))

    check_state(line_parts)


def check_config_file(fname):
    f = open(fname, 'r')

    print('[+] Checking "{}" against hardening preferences...'.format(fname))
    for line in f:
        opt_is_on = re.compile("CONFIG_[a-zA-Z0-9_]*=[a-zA-Z0-9_\"]*")
        opt_is_off = re.compile("# CONFIG_[a-zA-Z0-9_]* is not set")
        if opt_is_on.match(line):
            check_on(line[:-1]) # drop newline
        if opt_is_off.match(line):
            check_off(line[:-1]) # ditto

    print_check_results()
    f.close()


def usage(name):
    print('Usage: {} [-p | -c <config_file>] '.format(name))
    print(' -p, --print\n\tprint hardening preferences')
    print(' -c <config_file>, --config=<config_file>\n\tcheck the config_file against these preferences')
    sys.exit(1)


def main(argv):
    try:
        opts, args = getopt.getopt(argv[1:], 'pc:', ['print', 'config='])
    except getopt.GetoptError:
        usage(argv[0])

    if not opts:
        usage(argv[0])

    construct_opt_list()

    for opt, arg in opts:
        if opt in ('-p', '--print'):
            print_opt_list()
            sys.exit()
        elif opt in ('-c', '--config'):
            check_config_file(arg)
            if error_count == 0:
                print('[+] config check is PASSED')
            else:
                sys.exit('[-] config check is NOT PASSED: {} errors'.format(error_count))

main(sys.argv)
