from behave import given, when, then
import subprocess
import os

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

@when('I call the python script "{script}" with the command "{command}" and the public age key {public_key}')
def step_when_call_python_script(context, script, command, public_key):
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Join the current directory with the relative path provided in the feature file
    script_path = os.path.join(current_dir, script)
    command = f"python {script_path} {context.directory} --sops-config {context.sops_file}"
    context.output = subprocess.check_output(command, shell=True).decode()

@then('The output should contain this {list} of files')
def step_then_output_contains_list(context, list=None):
    matching_files = context.output.strip().split('\n')
    files = list.split(', ') if list else []
    for file in files:
        assert file in matching_files

@then('the output should not contain this {not_list} of files')
def step_then_output_not_contains_list(context, not_list):
    files = not_list.split(', ')
    for file in files:
        assert file not in context.output