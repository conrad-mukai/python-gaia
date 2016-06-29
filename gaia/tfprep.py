"""
gaia.tfprep
Preparation for running Terraform commands.
"""

# system imports
import os
import subprocess
import glob

# local imports
from check import check_requirements
from config import get_config, get_gaia_config

# map of AWS configuration parameters to environment variables
PARAM_TO_ENV_MAP = {
    'aws_access_key_id': 'AWS_ACCESS_KEY_ID',
    'aws_secret_access_key': 'AWS_SECRET_ACCESS_KEY',
    'region': 'AWS_DEFAULT_REGION'
}


def setup_terraform(terraform_home, aws_profile, glb, infrastructure,
                    environment, app_name, app_version, update):
    terraform_home = _get_terraform_home(terraform_home)
    region, app_name, s3_remote_bucket, terraform_dir \
        = _validate_inputs(terraform_home, aws_profile, glb, infrastructure,
                           app_name)
    _get_modules(terraform_dir, update)
    tfstate_path, app_version = _set_remote(terraform_dir, region, environment,
                                            app_name, app_version,
                                            s3_remote_bucket, glb,
                                            infrastructure)
    return terraform_dir, tfstate_path, app_version


def _get_terraform_home(terraform_home):
    if terraform_home:
        return terraform_home
    terraform_home = os.environ.get('TERRAFORM_HOME')
    if terraform_home:
        return terraform_home
    gaia_config = get_gaia_config()
    if not gaia_config \
       or not gaia_config.has_option('DEFAULT', 'terraform_home'):
        raise RuntimeError("terraform_home (TERRAFORM_HOME environment "
                           "variable) not specified")
    return gaia_config.get('DEFAULT', 'terraform_home')


def _validate_inputs(terraform_home, aws_profile, glb, infrastructure,
                     app_name):
    terraform_dir, region, hcl_app_name, s3_remote_bucket, aws_config_dir \
        = check_requirements(terraform_home, glb, infrastructure)
    app_name = _set_app_name(hcl_app_name, app_name)
    if aws_config_dir:
        aws_config = get_config(aws_config_dir, aws_profile)
        _set_environment(aws_config)
    _check_environment()
    return region, app_name, s3_remote_bucket, terraform_dir


def _set_app_name(hcl_app_name, app_name):
    # if app_name is set on the command line override what is in the Terraform
    # files
    if app_name:
        return app_name
    else:
        return hcl_app_name


def _set_environment(aws_config):
    for param, env_var in PARAM_TO_ENV_MAP.iteritems():
        if param not in aws_config:
            continue
        os.environ.setdefault(env_var, aws_config[param])


def _check_environment():
    for env_var in PARAM_TO_ENV_MAP.itervalues():
        if env_var not in os.environ:
            raise RuntimeError("%s environment variable not specified"
                               % env_var)


def _get_modules(terraform_dir, update):
    args = ['terraform', 'get']
    if update:
        args.append('-update')
    proc = subprocess.Popen(args, cwd=terraform_dir,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stderrdata = proc.communicate()[1]
    if proc.returncode != 0:
        raise RuntimeError("terraform get failed: %s" % stderrdata)


def _set_remote(terraform_dir, region, environment, app_name, app_version,
                s3_remote_bucket, glb, infrastructure):
    tf_config_dir = os.path.join(terraform_dir, '.terraform')
    app_version = _set_app_version(environment, app_version)
    tfstate_path = os.path.join(tf_config_dir,
                                _get_tfstate_name(environment, app_name,
                                                  app_version, glb,
                                                  infrastructure))
    if not os.path.exists(tfstate_path):
        if glb:
            s3_path = 'global'
        elif infrastructure:
            s3_path = 'infrastructure/%s/%s' % (app_name, environment)
        else:
            s3_path = 'applications/%s/%s' % (_get_app_id(app_name,
                                                          app_version),
                                              environment)
        s3_path += '/terraform.tfstate'
        proc = subprocess.Popen(['terraform', 'remote', 'config', '-backend=s3',
                                 '-backend-config',
                                 'bucket=%s' % s3_remote_bucket,
                                 '-backend-config', 'key=%s' % s3_path,
                                 '-backend-config', 'region=%s' % region],
                                cwd=terraform_dir, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        stderrdata = proc.communicate()[1]
        if proc.returncode != 0:
            raise RuntimeError("terraform remote config failed: %s"
                               % stderrdata)
        os.rename(os.path.join(tf_config_dir, 'terraform.tfstate'),
                  tfstate_path)
    return tfstate_path, app_version


def _set_app_version(environment, app_version):
    if not app_version and environment == 'sandbox':
        app_version = os.environ['USER']
    return app_version


def _get_tfstate_name(environment, app_name, app_version, glb, infrastructure):
    if glb:
        return 'terraform.tfstate'
    elif infrastructure:
        return 'terraform-%s-%s.tfstate' % (app_name, environment)
    else:   # application
        return 'terraform-%s-%s.tfstate' % (_get_app_id(app_name, app_version),
                                            environment)


def _get_app_id(app_name, app_version):
    if app_version:
        return '%s-%s' % (app_name, app_version)
    else:
        return app_name
