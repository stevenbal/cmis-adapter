import os
import sys

import invoke


@invoke.task
def clean(c):
    print('Clean uploads')
    c.run('rm -rf ./uploads')

    print('Clean tox')
    c.run('rm -rf ./.tox')

    print('Clean pytest')
    c.run('rm -rf ./.pytest_cache')


@invoke.task
def coverage(c):
    print('Run tests')
    c.run('coverage run runtests.py')
    print('Generate xml coverage')
    c.run('coverage xml')
    print('Show coverage')
    c.run('coverage report -m')


@invoke.task
def test(c, path=None):
    runtests([path])


def runtests(args=None):
    test_dir = os.path.dirname(__file__)
    sys.path.insert(0, test_dir)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'

    import django
    from django.test.utils import get_runner
    from django.conf import settings

    django.setup()

    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=1, interactive=True)
    args = args or ['.']
    failures = test_runner.run_tests(args)
    sys.exit(failures)
