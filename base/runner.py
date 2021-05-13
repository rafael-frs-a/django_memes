from django.conf import settings


class PytestTestRunner:
    def __init__(self, verbosity=1, failfast=False, keepdb=False, **kwargs):
        self.verbosity = verbosity
        self.failfast = failfast
        self.keepdb = keepdb
        settings.TEST_MODE = True
        settings.DEFAULT_FILE_STORAGE = 'inmemorystorage.InMemoryStorage'

    def run_tests(self, test_labels):
        import pytest

        argv = []

        if self.verbosity == 0:
            argv.append('--quiet')

        if self.verbosity == 2:
            argv.append('--verbose')

        if self.verbosity == 3:
            argv.append('-vv')

        if self.failfast:
            argv.append('--exitfirst')

        if self.keepdb:
            argv.append('--reuse-db')

        argv.extend(test_labels)
        return pytest.main(argv)
