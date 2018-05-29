import sys
import unittest

from pwclip.cmdline import confpars, cli, gui, PassCrypt

class TestPWClip(unittest.TestCase):
	def test_pwcli_list(self):
		sys.argv = ['pwcli', '-l']
		args, pargs, pkwargs = confpars('cli')
		ents = PassCrypt(*pargs, **pkwargs).lspw(args.lst)
		self.assertIsInstance(ents, dict)




if __name__ == '__main__':
    unittest.main()
