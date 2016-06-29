"""
gaia.driver
Main program driver.
"""

# local imports
from tfprep import setup_terraform
from tfexec import run_terraform

def run(args):
    terraform_dir, tfstate_path, app_version \
        = setup_terraform(args.terraform_home, args.aws_profile, args.glb,
                          args.infrastructure, args.environment, args.app_name,
                          args.app_version, args.update)
    run_terraform(args.command, args.environment, args.app_name,
                  app_version, args.glb, terraform_dir, tfstate_path)
