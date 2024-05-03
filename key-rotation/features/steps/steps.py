import parse
from behave import given, when, then, register_type
import subprocess
import os


@parse.with_pattern(r'.*')
def parse_nullable_string(text):
    return text


register_type(NullableString=parse_nullable_string)

@given('I have the sops configuration file "{sops_file}"')
def step_given_sops_config_file(context, sops_file):
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Join the current directory with the relative path provided in the feature file
    context.sops_file = os.path.join(current_dir, sops_file)

@given('I the file and folder structure "{directory}"')
def step_given_directory(context, directory):
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Join the current directory with the relative path provided in the feature file
    context.directory = os.path.join(current_dir, directory)

@when('I call the python script "{script}" with the following arguments')
def step_when_call_python_script(context, script):
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Join the current directory with the relative path provided in the feature file
    script_path = os.path.join(current_dir, script)

    # Construct the command
    command = f"python {script_path}"
    for row in context.table:
        arg_name = row['arg_name']
        arg_value = row['arg_value']
        if arg_name in ['--folder', '--sops-config']:
            arg_value = os.path.join(current_dir, arg_value)

        if arg_value:
            command += f" {arg_name} {arg_value}"
        else:
            command += f" {arg_name}"

    context.output = subprocess.check_output(command, shell=True).decode()

@then('The output should contain this {list:NullableString} of files')
def step_then_output_contains_list(context, list=None):
    if not list:
        assert len(context.output.strip()) == 0
        return
    matching_files = context.output.strip().split('\n')
    files = list.split(', ') if list else []
    for file in files:
        assert file in matching_files

@then('the output should not contain this {not_list:NullableString} of files')
def step_then_output_not_contains_list(context, not_list=None):
    if not not_list:
        return
    files = not_list.split(', ')
    for file in files:
        assert file not in context.output