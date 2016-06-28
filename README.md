# Gaia

Wrapper script to run Terraform.

## Usage

    usage: gaia [-h] [-g] [-i] [-a APP_NAME] [-v APP_VERSION] [-p AWS_PROFILE]
                [-t TERRAFORM_HOME]
                {apply,destroy,plan,show} [{sandbox,stage,prod}]
    
    build a CMX cloud
    
    positional arguments:
      {apply,destroy,plan,show}
                            terraform command
      {sandbox,stage,prod}  VPC type (do not use with -g)
    
    optional arguments:
      -h, --help            show this help message and exit
      -g, --global          execute global code--default is to execute application
                            code
      -i, --infrastructure  execute infrastructure code--default is to execute
                            application code
      -a APP_NAME, --app-name APP_NAME
                            override the app_name in the Terraform code
      -v APP_VERSION, --app-version APP_VERSION
                            specify an app version--defaults to username in
                            sandbox, and empty on others (appended to app_name)
      -p AWS_PROFILE, --profile AWS_PROFILE
                            AWS configuration profile
      -t TERRAFORM_HOME, --terraform-home TERRAFORM_HOME
                            directory containing terraform files