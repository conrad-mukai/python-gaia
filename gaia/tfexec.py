"""
gaia.tfexec
Module for running terraform commands.
"""

# system imports
import os
import subprocess


def run_terraform(command, environment, app_name, app_version, glb,
                  terraform_dir, tfstate_path):
    args = _create_args(command, environment, app_name, app_version, glb)
    tfstate_file = os.path.join(os.path.dirname(tfstate_path),
                                'terraform.tfstate')
    if tfstate_path != tfstate_file:
        os.rename(tfstate_path, tfstate_file)
    try:
        proc = subprocess.Popen(args, cwd=terraform_dir, stderr=subprocess.PIPE)
        stderrdata = proc.communicate()[1]
    finally:
        if tfstate_path != tfstate_file:
            os.rename(tfstate_file, tfstate_path)
    if proc.returncode != 0:
        raise RuntimeError("terraform %s failed:\n%s" % (command,
                                                         stderrdata))


def _create_args(command, environment, app_name, app_version, glb):
    args = ['terraform', command]
    if command == 'show':
        return args
    if glb:
        return args
    args += ['-var', 'environment=%s' % environment]
    if app_name:
        args += ['-var', 'app_name=%s' % app_name]
    if app_version:
        args += ['-var', 'app_version=-%s' % app_version]
    return args
