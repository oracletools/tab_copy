class Sorry(Exception):
  """
  Basic exception type for user errors; the traceback will be suppressed.
  """
  __orig_module__ = __module__
  # trick to get just "Sorry" instead of "libtbx.utils.Sorry"
  __module__ = Exception.__module__

  def reset_module (self) :
    self.__class__.__module__ = self.__class__.__orig_module__
	
class Abort(Sorry) :
  """
  Subclass of Sorry, primarily used in the Phenix GUI in response to user
  input.
  """
  __module__ = Exception.__module__
class multi_out(object):
  """
  Multiplexing output stream, e.g. for simultaneously printing to stdout
  and a logfile.
  """

  def __init__(self):
    self.labels = []
    self.file_objects = []
    self.atexit_send_to = []
    self.closed = False
    self.softspace = 0
    atexit.register(self._atexit)

  def _atexit(self):
    if (not self.closed):
      for f,a in zip(self.file_objects, self.atexit_send_to):
        if (a is not None): a.write(f.getvalue())

  def register(self, label, file_object, atexit_send_to=None):
    """Adds an output stream to the list."""
    assert not self.closed
    self.labels.append(label)
    self.file_objects.append(file_object)
    self.atexit_send_to.append(atexit_send_to)
    return self

  def replace_stringio(self,
        old_label,
        new_label,
        new_file_object,
        new_atexit_send_to=None):
    i = self.labels.index(old_label)
    old_file_object = self.file_objects[i]
    new_file_object.write(old_file_object.getvalue())
    old_file_object.close()
    self.labels[i] = new_label
    self.file_objects[i] = new_file_object
    self.atexit_send_to[i] = new_atexit_send_to

  def isatty(self):
    return False

  def close(self):
    for file_object in self.file_objects:
      if (file_object is sys.__stdout__): continue
      if (file_object is sys.__stderr__): continue
      file_object.close()
    self.closed = True

  def flush(self):
    for file_object in self.file_objects:
      flush = getattr(file_object, "flush", None)
      if (flush is not None): flush()

  def write(self, str):
    for file_object in self.file_objects:
      file_object.write(str)

  def writelines(self, sequence):
    for file_object in self.file_objects:
      file_object.writelines(sequence)

class host_and_user:

  def __init__(self):
    self.host = os.environ.get("HOST")
    self.hostname = os.environ.get("HOSTNAME")
    self.computername = os.environ.get("COMPUTERNAME")
    self.hosttype = os.environ.get("HOSTTYPE")
    self.processor_architecture = os.environ.get("PROCESSOR_ARCHITECTURE")
    self.machtype = os.environ.get("MACHTYPE")
    self.ostype = os.environ.get("OSTYPE")
    self.vendor = os.environ.get("VENDOR")
    self.user = os.environ.get("USER")
    self.username = os.environ.get("USERNAME")
    self.homedir = None
    if (os.name == "nt") :
      homedrive = os.environ.get("HOMEDRIVE")
      homepath = os.environ.get("HOMEPATH")
      if (not None in [homedrive, homepath]) :
        self.homedir = os.path.join(homedrive, homepath)
    else :
      self.homedir = os.environ.get("HOME")
    getpid = getattr(os, "getpid", None)
    if (getpid is None):
      self.pid = None
    else:
      self.pid = getpid()
    self.sge_info = sge_utils.info()
    self.pbs_info = pbs_utils.chunk_info()

  def get_user_name (self) :
    if (self.user is not None) :
      return self.user
    else :
      return self.username

  def get_host_name (self) :
    if (self.host is not None) :
      return self.host
    elif (self.hostname is not None) :
      return self.hostname
    elif (self.computername is not None) :
      return self.computername
    return None

  def show(self, out=None, prefix=""):
    if (out is None): out = sys.stdout
    if (self.host is not None):
      print >> out, prefix + "HOST =", self.host
    if (    self.hostname is not None
        and self.hostname != self.host):
      print >> out, prefix + "HOSTNAME =", self.hostname
    if (    self.computername is not None
        and self.computername != self.host):
      print >> out, prefix + "COMPUTERNAME =", self.computername
    if (self.hosttype is not None):
      print >> out, prefix + "HOSTTYPE =", self.hosttype
    if (self.processor_architecture is not None):
      print >> out, prefix + "PROCESSOR_ARCHITECTURE =", \
        self.processor_architecture
    if (   self.hosttype is None
        or self.machtype is None
        or self.ostype is None
        or "-".join([self.machtype, self.ostype]) != self.hosttype):
      if (self.machtype is not None):
        print >> out, prefix + "MACHTYPE =", \
          self.machtype
      if (self.ostype is not None):
        print >> out, prefix + "OSTYPE =", \
          self.ostype
    if (self.vendor is not None and self.vendor != "unknown"):
      print >> out, prefix + "VENDOR =", \
        self.vendor
    if (self.user is not None):
      print >> out, prefix + "USER =", self.user
    if (    self.username is not None
        and self.username != self.user):
      print >> out, prefix + "USERNAME =", self.username
    if (self.pid is not None):
      print >> out, prefix + "PID =", self.pid
    self.sge_info.show(out=out, prefix=prefix)
    self.pbs_info.show(out=out, prefix=prefix)
class detect_binary_file(object):

  def __init__(self, monitor_initial=None, max_fraction_non_ascii=None):
    if (monitor_initial is None):
      self.monitor_initial = 1000
    else:
      self.monitor_initial = monitor_initial
    if (max_fraction_non_ascii is None):
      self.max_fraction_non_ascii = 0.05
    else:
      self.max_fraction_non_ascii = max_fraction_non_ascii
    self.n_ascii_characters = 0
    self.n_non_ascii_characters = 0
    self.status = None

  def is_binary_file(self, block):
    if (self.monitor_initial > 0):
      for c in block:
        if (1 < ord(c) < 128):
          self.n_ascii_characters += 1
        else:
          self.n_non_ascii_characters += 1
        self.monitor_initial -= 1
        if (self.monitor_initial == 0):
          if (  self.n_non_ascii_characters
              > self.n_ascii_characters * self.max_fraction_non_ascii):
            self.status = True
          else:
            self.status = False
          break
    return self.status

  def from_initial_block(
        file_name,
        monitor_initial=None,
        max_fraction_non_ascii=None):
    detector = detect_binary_file(
      monitor_initial=monitor_initial,
      max_fraction_non_ascii=max_fraction_non_ascii)
    block = open(file_name, "rb").read(detector.monitor_initial)
    if (len(block) == 0): return False
    detector.monitor_initial = min(len(block), detector.monitor_initial)
    return detector.is_binary_file(block=block)
  from_initial_block = staticmethod(from_initial_block)
	  