import sys


class _Settings(object):
    def __getattr__(self, name):
        return globals()[name]


# other parts of itun that you WANT to code in
# module-ish ways
sys.modules[__name__] = _Settings()
