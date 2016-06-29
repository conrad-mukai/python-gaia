"""
cmxcloud.checks
Check program requirements.
"""

# system imports
import sys
import os
import subprocess


def check_requirements(terraform_home, glb, infrastructure):
    if not _check_program('terraform'):
        raise RuntimeError("terraform not found: see "
                           "https://www.terraform.io/intro/getting-started/"
                           "install.html")
    terraform_dir, region, app_name, s3_remote_bucket \
        = _check_tfcode(terraform_home, glb, infrastructure)
    aws_config_dir = _get_aws_config()
    return terraform_dir, region, app_name, s3_remote_bucket, aws_config_dir


def _check_program(prog_name):
    proc = subprocess.Popen(['which', prog_name], stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    proc.communicate()
    return proc.returncode == 0


def _check_tfcode(terraform_home, glb, infrastructure):
    if not os.path.isdir(terraform_home):
        raise RuntimeError("%s not found" % terraform_home)
    terraform_dir = _get_terraform_dir(terraform_home, glb, infrastructure)
    region, app_name, s3_remote_bucket = _get_hcl_variables(terraform_dir, glb,
                                                            infrastructure)
    return terraform_dir, region, app_name, s3_remote_bucket


def _get_terraform_dir(terraform_home, glb, infrastructure):
    if glb:
        terraform_dir = os.path.join(terraform_home, 'global')
        if not os.path.isdir(terraform_dir):
            raise RuntimeError("Terraform global code not found")
    elif infrastructure:
        terraform_dir = os.path.join(terraform_home, 'infrastructure')
        if not os.path.isdir(terraform_dir):
            raise RuntimeError("Terraform infrastructure code not found")
    else:   # application code
        terraform_dir = os.path.join(terraform_home, 'application')
        if not os.path.isdir(terraform_dir):
            raise RuntimeError("Terraform application code not found")
    return terraform_dir


def _get_hcl_variables(terraform_dir, glb, infrastructure):
    """
    Routine to read variables from Terraform code. Look for variable names in
    either variables.tf or terraform.tfvars. The order of precedence is:
      1. terraform.tfvars
      2. variables.tf

    Depending upon the variable we do different things if we find it or not.
    Required variables are app_name and s3_remote_bucket. If we find
    environment in one of the files then we issue a warning because it will be
    overridden by the command line option. If we find app_version we issue a
    warning because we don't want it to affect how stage and prod resources are
    tagged.
    """
    try:
        import hcl
    except ImportError:
        raise RuntimeError("pyhcl not installed: see "
                           "https://pypi.python.org/pypi/pyhcl")
    terraform_variables_path = os.path.join(terraform_dir, 'variables.tf')
    if os.path.exists(terraform_variables_path):
        with open(terraform_variables_path) as f:
            obj = hcl.load(f)
        variables = obj.get('variable')
        if not variables:
            raise RuntimeError("%s is not a variables file"
                               % terraform_variables_path)
    else:
        variables = None
    terraform_tfvars_path = os.path.join(terraform_dir, 'terraform.tfvars')
    if os.path.exists(terraform_tfvars_path):
        with open(terraform_tfvars_path) as f:
            tfvars = hcl.load(f)
    else:
        tfvars = None
    environment = _get_variable('environment', variables, tfvars)
    if environment:
        sys.stderr.write("[warning]: default environment in %s will not be "
                         "used\n" % terraform_variables_path)
    region = _get_variable('region', variables, tfvars)
    if not region:
        raise RuntimeError("value for region not found")
    app_name = _get_variable('app_name', variables, tfvars)
    if not app_name:
        raise RuntimeError("value for app_name not found")
    s3_remote_bucket = _get_variable('s3_remote_bucket', variables, tfvars)
    if not s3_remote_bucket:
        raise RuntimeError("value for s3_remote_bucket not found")
    if not glb and not infrastructure:  # application
        app_version = _get_variable('app_version', variables, tfvars)
        if app_version != '':
            sys.stderr.write("[warning]: app_version is hard coded in %s\n"
                             % terraform_variables_path)
    return region, app_name, s3_remote_bucket


def _get_variable(variable, variables, tfvars):
    if tfvars:
        var_obj = tfvars.get(variable)
        if var_obj:
            return var_obj
    if variables:
        var_obj = variables.get(variable)
        if var_obj:
            return var_obj.get('default')
    return None


def _get_aws_config():
    if _check_program('aws'):
        aws_config_dir = os.path.join(os.environ['HOME'], '.aws')
        if not os.path.isdir(aws_config_dir) \
           or not os.path.exists(os.path.join(aws_config_dir, 'credentials')):
            return None
        return aws_config_dir
    else:
        return None
