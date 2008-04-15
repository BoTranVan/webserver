import os
import base64
from base import *

USER="cherokeeqa"
PASS="invalid"

CONF = """
vserver!default!rule!620!match!type = directory
vserver!default!rule!620!match!directory = /privpam2
vserver!default!rule!620!match!final = 0
vserver!default!rule!620!auth = pam
vserver!default!rule!620!auth!methods = basic
vserver!default!rule!620!auth!realm = Test PAM
"""

class Test (TestBase):
    def __init__ (self):
        TestBase.__init__ (self)
        self.name             = "Auth PAM, reject"

        # Build the authentication string
        auth = base64.encodestring("%s:%s" % (USER,PASS))
        if auth[-1] == "\n": auth = auth[:-1]

        self.request          = "GET /privpam2/ HTTP/1.0\r\n" + \
                                "Authorization: Basic %s\r\n" % (auth)
        self.expected_error   = 401

    def Prepare (self, www):
        if not self.Precondition():
            return

        directory = self.Mkdir (www, "privpam2")
        self.conf = CONF

    def Precondition (self):
        # It will only work it the server runs as root
        if os.getuid() != 0:
            return False

        try: 
            # Check that pam module was compiled
            pams = filter(lambda x: "pam" in x, os.listdir(CHEROKEE_MODS))
            if len(pams) < 1:
                return False

            # Read the /etc/passwd file
            f = open ("/etc/passwd", "r")
            pwuser = filter(lambda x: x.find(USER) == 0, f.readlines())
            f.close
        except:
            return False

        # Sanity check
        if len(pwuser) is not 1:
            return False

        return True
