#!/usr/bin/python
# iotop: Display I/O usage of processes in a top like UI
# Copyright (c) 2007 Guillaume Chazarain <guichaz@yahoo.fr>, GPLv2
# See ./iotop.py --help for some help

# 20070723: Added support for taskstats version > 4
# 20070813: Handle short replies, and fix bandwidth calculation when delay != 1s
# 20070819: Fix "-P -p NOT_A_TGID", optimize -p, handle empty process list
# 20070825: More accurate cutting of the command line, handle terminal resizing
# 20070826: Document taskstats bug: http://lkml.org/lkml/2007/8/2/185
# 20070930: Fixed -b

import curses
import errno
import optparse
import os
import pwd
import select
import socket
import struct
import sys
import time

#
# Check for requirements:
#   o Python >= 2.5 for AF_NETLINK sockets
#   o Linux >= 2.6.20 with I/O accounting
#
try:
    socket.NETLINK_ROUTE
    python25 = True
except AttributeError:
    python25 = False

ioaccounting = os.path.exists('/proc/self/io')

if not python25 or not ioaccounting:
    def boolean2string(boolean):
        return boolean and 'Found' or 'Not found'
    print 'Could not run iotop as some of the requirements are not met:'
    print '- Python >= 2.5 for AF_NETLINK support:', boolean2string(python25)
    print '- Linux >= 2.6.20 with I/O accounting support:', \
          boolean2string(ioaccounting)
    sys.exit(1)

#
# Netlink stuff
# Based on code from pynl80211: Netlink message generation/parsing
# http://git.sipsolutions.net/?p=pynl80211.git
# Copyright 2007 Johannes Berg <johannes@sipsolutions.net>
# GPLv2

# flags
NLM_F_REQUEST = 1

# types
NLMSG_ERROR = 2
NLMSG_MIN_TYPE = 0x10

class Attr:
    def __init__(self, type, str, *kw):
        self.type = type
        if len(kw):
            self.data = struct.pack(str, *kw)
        else:
            self.data = str

    def _dump(self):
        hdr = struct.pack('HH', len(self.data)+4, self.type)
        length = len(self.data)
        pad = ((length + 4 - 1) & ~3 ) - length
        return hdr + self.data + '\0' * pad

    def u16(self):
        return struct.unpack('H', self.data)[0]

class NulStrAttr(Attr):
    def __init__(self, type, str):
        Attr.__init__(self, type, '%dsB'%len(str), str, 0)

class U32Attr(Attr):
    def __init__(self, type, val):
        Attr.__init__(self, type, 'L', val)

NETLINK_GENERIC = 16

class Message:
    def __init__(self, tp, flags = 0, seq = -1, payload = []):
        self.type = tp
        self.flags = flags
        self.seq = seq
        self.pid = -1
        if type(payload) == list:
            contents = []
            for attr in payload:
                contents.append(attr._dump())
            self.payload = ''.join(contents)
        else:
            self.payload = payload

    def send(self, conn):
        if self.seq == -1:
            self.seq = conn.seq()

        self.pid = conn.pid
        length = len(self.payload)

        hdr = struct.pack('IHHII', length + 4*4, self.type, self.flags,
                          self.seq, self.pid)
        conn.send(hdr + self.payload)

class Connection:
    def __init__(self, nltype, groups=0, unexpected_msg_handler = None):
        self.fd = socket.socket(socket.AF_NETLINK, socket.SOCK_RAW, nltype)
        self.fd.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536)
        self.fd.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)
        self.fd.bind((0, groups))
        self.pid, self.groups = self.fd.getsockname()
        self._seq = 0
        self.unexpected = unexpected_msg_handler

    def send(self, msg):
        self.fd.send(msg)

    def recv(self):
        cntnts = self.fd.recv(65536)
        # should check msgflags for TRUNC!
        len, type, flags, seq, pid = struct.unpack('IHHII', cntnts[:16])
        m = Message(type, flags, seq, cntnts[16:])
        m.pid = pid
        if m.type == NLMSG_ERROR:
            errno = -struct.unpack('i', m.payload[:4])[0]
            if errno != 0:
                e = OSError('Netlink error: %s (%d)' % \
                                                    (os.strerror(errno), errno))
                e.errno = errno
        return m

    def seq(self):
        self._seq += 1
        return self._seq

def parse_attributes(str):
    attrs = {}
    while str:
        l, tp = struct.unpack('HH', str[:4])
        attrs[tp] = Attr(tp, str[4:l])
        l = ((l + 4 - 1) & ~3 )
        str = str[l:]
    return attrs

CTRL_CMD_GETFAMILY = 3

CTRL_ATTR_FAMILY_ID = 1
CTRL_ATTR_FAMILY_NAME = 2

class GenlHdr:
    def __init__(self, cmd, version = 0):
        self.cmd = cmd
        self.version = version

    def _dump(self):
        return struct.pack('BBxx', self.cmd, self.version)

def _genl_hdr_parse(data):
    return GenlHdr(*struct.unpack('BBxx', data))

GENL_ID_CTRL = NLMSG_MIN_TYPE

class GeNlMessage(Message):
    def __init__(self, family, cmd, attrs=[], flags=0):
        self.cmd = cmd
        self.attrs = attrs
        self.family = family
        Message.__init__(self, family, flags=flags,
                         payload=[GenlHdr(self.cmd)] + attrs)

class Controller:
    def __init__(self, conn):
        self.conn = conn

    def get_family_id(self, family):
        a = NulStrAttr(CTRL_ATTR_FAMILY_NAME, family)
        m = GeNlMessage(GENL_ID_CTRL, CTRL_CMD_GETFAMILY,
                        flags=NLM_F_REQUEST, attrs=[a])
        m.send(self.conn)
        m = self.conn.recv()
        gh = _genl_hdr_parse(m.payload[:4])
        attrs = parse_attributes(m.payload[4:])
        return attrs[CTRL_ATTR_FAMILY_ID].u16()

#
# Netlink usage for taskstats
#

TASKSTATS_CMD_GET = 1
TASKSTATS_CMD_ATTR_PID = 1
TASKSTATS_CMD_ATTR_TGID = 2

class TaskStatsNetlink(object):
    # Keep in sync with human_stats(stats, duration)
    members_offsets = [
        ('blkio_delay_total', 40),
        ('swapin_delay_total', 56),
        ('ac_etime', 144),
        ('read_bytes', 248),
        ('write_bytes', 256),
        ('cancelled_write_bytes', 264)
    ]

    def __init__(self, options):
        self.options = options
        self.connection = Connection(NETLINK_GENERIC)
        controller = Controller(self.connection)
        self.family_id = controller.get_family_id('TASKSTATS')

    def get_task_stats(self, pid):
        if self.options.processes:
            attr = TASKSTATS_CMD_ATTR_TGID
        else:
            attr = TASKSTATS_CMD_ATTR_PID
        request = GeNlMessage(self.family_id, cmd=TASKSTATS_CMD_GET,
                              attrs=[U32Attr(attr, pid)],
                              flags=NLM_F_REQUEST)
        request.send(self.connection)
        try:
            reply = self.connection.recv()
        except OSError, e:
            if e.errno == errno.ESRCH:
                # OSError: Netlink error: No such process (3)
                return
            raise
        if len(reply.payload) < 292:
            # Short reply
            return
        reply_data = reply.payload[20:]

        reply_length, reply_type = struct.unpack('HH', reply.payload[4:8])
        reply_version = struct.unpack('H', reply.payload[20:22])[0]
        assert reply_length >= 288
        assert reply_type == attr + 3
        assert reply_version >= 4

        res = {}
        for name, offset in TaskStatsNetlink.members_offsets:
            data = reply_data[offset: offset + 8]
            res[name] = struct.unpack('Q', data)[0]

        return res

#
# PIDs manipulations
#

def find_uids(options):
    options.uids = []
    error = False
    for u in options.users or []:
        try:
            uid = int(u)
        except ValueError:
            try:
                passwd = pwd.getpwnam(u)
            except KeyError:
                print >> sys.stderr, 'Unknown user:', u
                error = True
            else:
                uid = passwd.pw_uid
        if not error:
            options.uids.append(uid)
    if error:
        sys.exit(1)

class pinfo(object):
    def __init__(self, pid, options):
        self.mark = False
        self.pid = pid
        self.stats = {}
        for name, offset in TaskStatsNetlink.members_offsets:
            self.stats[name] = (0, 0) # Total, Delta
        self.parse_status('/proc/%d/status' % pid, options)

    def check_if_valid(self, uid, options):
        self.valid = options.pids or not options.uids or uid in options.uids

    def parse_status(self, path, options):
        for line in open(path):
            if line.startswith('Name:'):
                # Name kernel threads
                self.name = '[' + line.split()[1].strip() + ']'
            elif line.startswith('Uid:'):
                uid = int(line.split()[1])
                # We check monitored PIDs only here
                self.check_if_valid(uid, options)
                try:
                    self.user = pwd.getpwuid(uid).pw_name
                except KeyError:
                    self.user = str(uid)
                break

    def add_stats(self, stats):
        self.stats_timestamp = time.time()
        for name, value in stats.iteritems():
            prev_value = self.stats[name][0]
            self.stats[name] = (value, value - prev_value)

    def get_cmdline(self):
        # A process may exec, so we must always reread its cmdline
        try:
            proc_cmdline = open('/proc/%d/cmdline' % self.pid)
        except IOError:
            return '{no such process}'
        cmdline = proc_cmdline.read(4096)
        parts = cmdline.split('\0')
        first_command_char = parts[0].rfind('/') + 1
        parts[0] = parts[0][first_command_char:]
        cmdline = ' '.join(parts).strip()
        return cmdline.encode('string_escape') or self.name

class ProcessList(object):
    def __init__(self, taskstats_connection, options):
        # {pid: pinfo}
        self.processes = {}
        self.taskstats_connection = taskstats_connection
        self.options = options

        # A first time as we are interested in the delta
        self.update_process_counts()

    def get_process(self, pid):
        process = self.processes.get(pid, None)
        if not process:
            try:
                process = pinfo(pid, self.options)
            except IOError:
                # IOError: [Errno 2] No such file or directory: '/proc/...'
                return
            if not process.valid:
                return
            self.processes[pid] = process
        return process

    def list_pids(self, tgid):
        if self.options.processes or self.options.pids:
            return [tgid]
        try:
            return map(int, os.listdir('/proc/%d/task' % tgid))
        except OSError:
            return []

    def update_process_counts(self):
        total_read = total_write = duration = 0
        tgids = self.options.pids or [int(tgid) for tgid in os.listdir('/proc')
                                      if '0' <= tgid[0] and tgid[0] <= '9']
        for tgid in tgids:
            for pid in self.list_pids(tgid):
                process = self.get_process(pid)
                if process:
                    stats = self.taskstats_connection.get_task_stats(pid)
                    if stats:
                        process.mark = False
                        process.add_stats(stats)
                        total_read += process.stats['read_bytes'][1]
                        total_write += process.stats['write_bytes'][1]
                        if not duration:
                            duration = process.stats['ac_etime'][1] / 1000000.0
        return total_read, total_write, duration

    def refresh_processes(self):
        for process in self.processes.values():
            process.mark = True
        total_read_and_write_and_duration = self.update_process_counts()
        to_delete = []
        for pid, process in self.processes.iteritems():
            if process.mark:
                to_delete.append(pid)
        for pid in to_delete:
            del self.processes[pid]
        return total_read_and_write_and_duration

#
# Utility functions for the UI
#

UNITS = ['B', 'K', 'M', 'G', 'T', 'P', 'E']

def human_bandwidth(size, duration):
    bw = size and float(size) / duration
    for i in xrange(len(UNITS) - 1, 0, -1):
        base = 1 << (10 * i)
        if 2 * base < size:
            res = '%.2f %s' % ((float(bw) / base), UNITS[i])
            break
    else:
        res = str(bw) + ' ' + UNITS[0]
    return res + '/s'

def human_stats(stats):
    # Keep in sync with TaskStatsNetlink.members_offsets and
    # IOTopUI.get_data(self)
    duration = stats['ac_etime'][1] / 1000000.0
    def delay2percent(name): # delay in ns, duration in s
        if not duration:
            return 'KERNBUG'
        return '%.2f %%' % min(99.99, stats[name][1] / (duration * 10000000.0))
    io_delay = delay2percent('blkio_delay_total')
    swapin_delay = delay2percent('swapin_delay_total')
    read_bytes = human_bandwidth(stats['read_bytes'][1], duration)
    written_bytes = stats['write_bytes'][1] - stats['cancelled_write_bytes'][1]
    written_bytes = max(0, written_bytes)
    write_bytes = human_bandwidth(written_bytes, duration)
    return io_delay, swapin_delay, read_bytes, write_bytes

#
# The UI
#

class IOTopUI(object):
    # key, reverse
    sorting_keys = [
        (lambda p: p.pid, False),
        (lambda p: p.user, False),
        (lambda p: p.stats['read_bytes'][1], True),
        (lambda p: p.stats['write_bytes'][1] -
                   p.stats['cancelled_write_bytes'][1], True),
        (lambda p: p.stats['swapin_delay_total'][1], True),
        # The default sorting (by I/O % time) should show processes doing
        # only writes, without waiting on them
        (lambda p: p.stats['blkio_delay_total'][1] or
                   int(not(not(p.stats['read_bytes'][1] or
                               p.stats['write_bytes'][1]))), True),
        (lambda p: p.get_cmdline(), False),
    ]

    def __init__(self, win, process_list, options):
        self.process_list = process_list
        self.options = options
        self.sorting_key = 5
        self.sorting_reverse = IOTopUI.sorting_keys[5][1]
        if not self.options.batch:
            self.win = win
            self.resize()
            curses.use_default_colors()
            curses.start_color()
            curses.curs_set(0)

    def resize(self):
        self.height, self.width = self.win.getmaxyx()

    def run(self):
        iterations = 0
        poll = select.poll()
        if not self.options.batch:
            poll.register(sys.stdin.fileno(), select.POLLIN|select.POLLPRI)
        while self.options.iterations is None or \
              iterations < self.options.iterations:
            total = self.process_list.refresh_processes()
            total_read, total_write, duration = total
            self.refresh_display(total_read, total_write, duration)
            if self.options.iterations is not None:
                iterations += 1
                if iterations >= self.options.iterations:
                    break

            try:
                events = poll.poll(self.options.delay_seconds * 1000.0)
            except select.error, e:
                if e.args and e.args[0] == errno.EINTR:
                    events = 0
                else:
                    raise
            if not self.options.batch:
                self.resize()
            if events:
                key = self.win.getch()
                self.handle_key(key)

    def reverse_sorting(self):
        self.sorting_reverse = not self.sorting_reverse

    def adjust_sorting_key(self, delta):
        orig_sorting_key = self.sorting_key
        self.sorting_key += delta
        self.sorting_key = max(0, self.sorting_key)
        self.sorting_key = min(len(IOTopUI.sorting_keys) - 1, self.sorting_key)
        if orig_sorting_key != self.sorting_key:
            self.sorting_reverse = IOTopUI.sorting_keys[self.sorting_key][1]

    def handle_key(self, key):
        key_bindings = {
            ord('q'):
                lambda: sys.exit(0),
            ord('Q'):
                lambda: sys.exit(0),
            ord('r'):
                lambda: self.reverse_sorting(),
            ord('R'):
                lambda: self.reverse_sorting(),
            curses.KEY_LEFT:
                lambda: self.adjust_sorting_key(-1),
            curses.KEY_RIGHT:
                lambda: self.adjust_sorting_key(1),
            curses.KEY_HOME:
                lambda: self.adjust_sorting_key(-len(IOTopUI.sorting_keys)),
            curses.KEY_END:
                lambda: self.adjust_sorting_key(len(IOTopUI.sorting_keys))
        }

        action = key_bindings.get(key, lambda: None)
        action()

    def get_data(self):
        def format(p):
            stats = human_stats(p.stats)
            io_delay, swapin_delay, read_bytes, write_bytes = stats
            line = '%5d %-8s %11s %11s %7s %7s ' % (p.pid, p.user[:8],
                                read_bytes, write_bytes, swapin_delay, io_delay)
            if self.options.batch:
                max_cmdline_length = 4096
            else:
                max_cmdline_length = self.width - len(line)
            line += p.get_cmdline()[:max_cmdline_length]
            return line

        processes = self.process_list.processes.values()
        key = IOTopUI.sorting_keys[self.sorting_key][0]
        processes.sort(key=key, reverse=self.sorting_reverse)
        if not self.options.batch:
            del processes[self.height - 2:]
        return map(format, processes)

    def refresh_display(self, total_read, total_write, duration):
        summary = 'Total DISK READ: %s | Total DISK WRITE: %s' % (
                                        human_bandwidth(total_read, duration),
                                        human_bandwidth(total_write, duration))
        titles = ['  PID', ' USER', '      DISK READ', '  DISK WRITE',
                  '   SWAPIN', '    IO', '    COMMAND']
        lines = self.get_data()
        if self.options.batch:
            print summary
            print ''.join(titles)
            for l in lines:
                print l
        else:
            self.win.clear()
            self.win.addstr(summary)
            self.win.hline(1, 0, ord(' ') | curses.A_REVERSE, self.width)
            for i in xrange(len(titles)):
                attr = curses.A_REVERSE
                title = titles[i]
                if i == self.sorting_key:
                    attr |= curses.A_BOLD
                    title += self.sorting_reverse and '>' or '<'
                self.win.addstr(title, attr)
            for i in xrange(len(lines)):
                self.win.insstr(i + 2, 0, lines[i])
            self.win.refresh()

def run_iotop(win, options):
    taskstats_connection = TaskStatsNetlink(options)
    process_list = ProcessList(taskstats_connection, options)
    ui = IOTopUI(win, process_list, options)
    ui.run()

#
# Main program
#

VERSION = '0.1'

USAGE = 'Usage: %s [OPTIONS]' % sys.argv[0] + '''

DISK READ and DISK WRITE are the block I/O bandwidth used during the sampling
period. SWAPIN and IO are the percentages of time the thread spent respectively
while swapping in and waiting on I/O more generally.
Controls: left and right arrows to should the sorting column, r to invert the
sorting order, q to quit, any other key to force a refresh'''

def main():
    parser = optparse.OptionParser(usage=USAGE, version='iotop ' + VERSION)
    parser.add_option('-d', '--delay', type='float', dest='delay_seconds',
                      help='delay between iterations [1 second]',
                      metavar='SEC', default=1)
    parser.add_option('-p', '--pid', type='int', dest='pids', action='append',
                      help='processes to monitor [all]', metavar='PID')
    parser.add_option('-u', '--user', type='str', dest='users', action='append',
                      help='users to monitor [all]', metavar='USER')
    parser.add_option('-b', '--batch', action='store_true', dest='batch',
                      help='non-interactive mode')
    parser.add_option('-P', '--processes', action='store_true',
                      dest='processes',
                      help='show only processes, not all threads')
    parser.add_option('-n', '--iter', type='int', dest='iterations',
                      metavar='NUM',
                      help='number of iterations before ending [infinite]')
    options, args = parser.parse_args()
    if args:
        parser.error('Unexpected arguments: ' + ' '.join(args))
    find_uids(options)
    options.pids = options.pids or []
    if options.batch:
        run_iotop(None, options)
    else:
        curses.wrapper(run_iotop, options)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    sys.exit(0)

