#!/usr/bin/env python3
from json import dumps as encode_json, loads as decode_json
from sys import stderr
from subprocess import Popen, PIPE, STDOUT
from base64 import decodestring as decode_base64
from logging import getLogger, StreamHandler, Formatter, DEBUG, INFO
from llfuse import Operations, FUSEError, EntryAttributes, ROOT_INODE, main as fuse_main, init as fuse_init, close as fuse_close
try:
	from llfuse import default_options
except ImportError:
	default_options = frozenset({'default_permissions', 'no_splice_read', 'big_writes', 'splice_move', 'nonempty', 'splice_write'})

try:
	import faulthandler
except ImportError:
	print("not faulthandler")
else:
	faulthandler.enable()

log = getLogger(__name__)

class VmReadFS(Operations):
	def __init__(self, targetvm, debug):
		super(VmReadFS, self).__init__()
		self.daemon = Popen(
			['python3', 'usr/bin/QubesInterVMFSd.py', ] if debug else
			['qrexec-client-vm', targetvm, 'qubes.QubesInterVMFS', ]
			, stdout=PIPE, stdin=PIPE, )

	def _send_receive(self, msg):
		self.daemon.stdin.write(bytes(encode_json(msg) + '\n', 'utf-8'))
		self.daemon.stdin.flush()
		msg = decode_json(str(self.daemon.stdout.readline(), 'utf-8'))
		if 'error' in msg:
			raise FUSEError(msg['error'][0])
		return msg['result']

	def _attr2entry(self, attr):
		entry = EntryAttributes()
		for k in (
			#'attr_timeout',
			#'entry_timeout',
			#'generation',
			'st_atime_ns',
			#'st_blksize',
			#'st_blocks',
			'st_ctime_ns',
			'st_gid',
			'st_ino',
			'st_mode',
			#'st_mtime',
			'st_mtime_ns',
			'st_nlink',
			#'st_rdev',
			'st_size',
			'st_uid',
			):
			v = attr.pop(k)
			setattr(entry, k, v)
		assert not attr, attr
		return entry

	def debug(self, debug):
		return self._send_receive(dict(debug=(debug, )))

	def opendir(self, inode, ctx):
		msg = self._send_receive(dict(opendir=(inode, dict(pid=ctx.pid, uid=ctx.uid, gid=ctx.gid, umask=ctx.umask, isroot=inode==ROOT_INODE, ))))
		return msg

	def readdir(self, fh, off):
		msg = self._send_receive(dict(readdir=(fh, off)))
		for name, attr, index in msg:
			yield (bytes(name, 'utf-8'), self._attr2entry(attr), index)

	def releasedir(self, inode):
		msg = self._send_receive(dict(releasedir=(inode, )))
		return msg

	def getattr(self, inode, ctx):
		msg = self._send_receive(dict(getattr=(inode, dict(pid=ctx.pid, uid=ctx.uid, gid=ctx.gid, umask=ctx.umask, isroot=inode==ROOT_INODE, ), )))
		return self._attr2entry(msg)

	def lookup(self, parent_inode, name, ctx):
		msg = self._send_receive(dict(lookup=(parent_inode, str(name, 'utf-8'), dict(pid=ctx.pid, uid=ctx.uid, gid=ctx.gid, umask=ctx.umask, isroot=parent_inode==ROOT_INODE, ))))
		return self._attr2entry(msg)

	def open(self, inode, flags, ctx):
		msg = self._send_receive(dict(open=(inode, flags, dict(pid=ctx.pid, uid=ctx.uid, gid=ctx.gid, umask=ctx.umask, isroot=inode==ROOT_INODE, ))))
		return msg

	def read(self, fh, off, size):
		msg = self._send_receive(dict(read=(fh, off, size)))
		return decode_base64(bytes(msg, 'ascii'))

	def flush(self, fh):
		msg = self._send_receive(dict(flush=(fh, )))
		return msg

	def release(self, fh):
		msg = self._send_receive(dict(release=(fh, )))
		return msg


def init_logging(debug=False):
	handler = StreamHandler(stderr)
	handler.setFormatter(Formatter('%(asctime)s.%(msecs)03d %(threadName)s: [%(name)s] %(message)s', datefmt="%Y-%m-%d %H:%M:%S"))
	root_logger = getLogger()
	if debug:
		handler.setLevel(DEBUG)
		root_logger.setLevel(DEBUG)
	else:
		handler.setLevel(INFO)
		root_logger.setLevel(INFO)
	root_logger.addHandler(handler)

def main(targetvm, mountpoint, debug=0):
	debug = int(debug)
	init_logging(debug)
	testfs = VmReadFS(targetvm, debug)
	testfs.debug(debug)
	fuse_options = set(default_options)
	fuse_options.add('fsname=qubes.QubesInterVMFS')
	if debug:
		fuse_options.add('debug')
	fuse_init(testfs, mountpoint, fuse_options)
	try:
		fuse_main(workers=1)
	finally:
		fuse_close()

if __name__ == '__main__':
	from sys import argv
	main(*argv[1:])
# vim:tw=0:nowrap
