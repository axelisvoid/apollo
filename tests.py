import unittest
from main import isroot, comm, rm_apt_warning, rmstr, RootUserExpectedError


class TestsAuxiliaryFunctions(unittest.TestCase):
  """."""

  def test_isroot(self):
    # will fail if ran with sudo
    self.assertEqual(isroot(), False)


  def test_comm(self):
    cmd = "echo \"Hello\""
    outs, errs = comm(cmd)

    self.assertEqual(outs, b"\"Hello\"\n")
    self.assertEqual(errs, b"")
  
  
  def test_rmstr(self):
    
    dummy_str = b"The quick brown fox jumps over the lazy dog"
    dummy_str_t3 = dummy_str * 3  # times 3

    self.assertEqual(rmstr(dummy_str, dummy_str_t3), b"")
  

  def test_rm_apt_warning(self):
    
    if not isroot():
      raise RootUserExpectedError("This test can only work when user has been set as root.")

    cmd = "apt update"
    outs, errs = comm(cmd)

    self.assertNotEqual(outs, None, b"")
    self.assertNotEqual(errs, None, b"")

    if errs:
      errs_ = rm_apt_warning(errs)
      self.assertEqual(errs_, b"")

    
if __name__ == "__main__":
  unittest.main()