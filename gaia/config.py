"""
gaia.config
Module to return program configuration. This is generally stuff from AWS CLI
configuration.
"""

# system imports
import os
import ConfigParser


def get_gaia_config():
    gaia_config_path = os.path.join(os.environ['HOME'], '.gaia', 'config')
    if os.path.exists(gaia_config_path):
        parser = ConfigParser.SafeConfigParser()
        parsed_files = parser.read(gaia_config_path)
        if len(parsed_files) != 1:
            raise SyntaxError("syntax error in %s" % gaia_config_path)
        return parser
    else:
        return None


def get_config(aws_config_dir, aws_profile):
    config_files = _get_aws_config_files(aws_config_dir)
    parser = ConfigParser.SafeConfigParser()
    parsed_files = parser.read(config_files)
    if len(parsed_files) != len(config_files):
        raise RuntimeError("the following files could not be parsed: %s"
                           % ','.join(f for f in config_files
                                      if f not in parsed_files))
    try:
        aws_config = dict(parser.items('default'))
    except ConfigParser.NoSectionError:
        pass
    if aws_profile:
        try:
            aws_config.update(parser.items(aws_profile))
        except ConfigParser.NoSectionError:
            raise RuntimeError("no %s profile in AWS configuration"
                               % aws_profile)
    return aws_config


def _get_aws_config_files(aws_config_dir):
    config_files = [os.path.join(aws_config_dir, 'credentials')]
    aws_config_file = os.path.join(aws_config_dir, 'config')
    if os.path.exists(aws_config_file):
        config_files.append(aws_config_file)
    return config_files
