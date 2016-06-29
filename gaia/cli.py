"""
gaia.cli
Module for the command line interface.
"""

# system imports
import sys
import argparse

# local imports
from driver import run


def main(argv=sys.argv):
    try:
        args = _parse_args(argv)
        run(args)
    except SystemExit, e:
        return e
    except Exception, e:
        sys.stderr.write("[error]: %s\n" % e)
        return 1
    return 0


def _parse_args(argv):
    parser = argparse.ArgumentParser(description="build a CMX cloud")
    parser.add_argument('-g', '--global', dest='glb', action='store_true',
                        help="execute global code--default is to execute "
                             "application code")
    parser.add_argument('-i', '--infrastructure', action='store_true',
                        help="execute infrastructure code--default is to "
                             "execute application code")
    parser.add_argument('-a', '--app-name', dest='app_name',
                        help="override the app_name in the Terraform code")
    parser.add_argument('-v', '--app-version', dest='app_version',
                        help="specify an app version--defaults to username in "
                             "sandbox, and empty on others (appended to "
                             "app_name)")
    parser.add_argument('-p', '--profile', dest='aws_profile',
                        default=None, help="AWS configuration profile")
    parser.add_argument('-t', '--terraform-home', dest='terraform_home',
                        help="directory containing terraform files")
    parser.add_argument('-u', '--update', action='store_true',
                        help="update all terraform modules before running "
                             "command")
    parser.add_argument('command', choices=('apply', 'destroy', 'plan', 'show'),
                        help="terraform command")
    parser.add_argument('environment', choices=('sandbox', 'stage', 'prod'),
                        nargs='?', default=None,
                        help="VPC type (do not use with -g)")
    args = parser.parse_args(argv[1:])
    if args.glb and args.infrastructure:
        raise RuntimeError("-g and -i options are mutually exclusive")
    if args.glb:
        if args.environment:
            raise RuntimeError("environment not allowed with -g option")
        if args.app_name or args.app_version:
            sys.stderr.write("[warning]: -a and -v ignored with -g option\n")
    else:
        if not args.environment:
            raise RuntimeError("environment not specified")
    return args
