"""system.agentinfo library"""
from os import \
    getuid, environ, \
    getenv, stat as osstat
from os.path import exists

from stat import S_ISSOCK as issock

from system.user import userfind

def gpgagentinfo():
	"""gpg-agent socket finder function"""
	uid = getenv('SUDO_UID')
	if not uid:
		uid = getuid()
	rundir = '/run/user/%s/gnupg'%uid
	gpgsock = '%s/S.gpg-agent'%rundir
	sshsock = '%s/S.gpg-agent.ssh'%rundir
	if not exists(gpgsock) or not issock(osstat(gpgsock).st_mode):
		usrhome = userfind(uid, 'home')
		gpgsock = '%s/.gnupg/S.gpg-agent'%usrhome
		sshsock = '%s/.gnupg/S.gpg-agent.ssh'%usrhome
	environ['GPG_AGENT_INFO'] = gpgsock
	environ['SSH_AUTH_SOCK'] = sshsock
	return gpgsock, sshsock
