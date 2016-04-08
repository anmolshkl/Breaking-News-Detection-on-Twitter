import string
import utils

def isAscii(s):
    try:
        s.encode('ascii')
        return True
    except (UnicodeDecodeError, UnicodeEncodeError):
        return False

class Tweet:
    def __init__(self, msg, timestamp, msgid, uid):
        self.msg       = utils.cleanThis(msg)
        self.timestamp = timestamp
        self.msgid     = msgid
        self.vector    = None
        self.uid       = uid
        self.tokens    = None
        self.tags      = None

    def __str__(self):
        return str(self.timestamp) + ':' + self.msg

    def getTokens(self):
        if self.tokens == None:
            tok = []
            for t in self.msg.lower().split():
                if isAscii(t) and not ('http' in t or t.startswith('#') or t.startswith('@')):
                    t = t.translate({ord(c): None for c in string.punctuation})
                    if len(t) > 0:
                        tok.append(t)
            self.tokens = tok
        return self.tokens

    def getHashTags(self):
        if self.tags == None:
            tag_list = []
            for w in self.msg.lower().split():
                if w.startswith('#') and len(w) > 1:
                    tag_list.append(w)
            self.tags = tag_list
        return self.tags

    def setVector(self, vec):
        self.vector = vec

    def getVector(self):
        if self.vector:
            return self.vector
        else:
            return {}

