import parse
from behave import given, when, then, register_type, use_step_matcher
import subprocess
import os
import shutil
import tempfile
import yaml

use_step_matcher("re")


@parse.with_pattern(r'.*')
def parse_nullable_string(text):
    return text


register_type(NullableString=parse_nullable_string)


def add_named_attribute_to_context(context, name, value):
    if getattr(context, 'named_attributes', None) is None or context.named_attributes is None:
        context.named_attributes = {}
    context.named_attributes[name] = value


@given(u'I create a copy of the folder "(?P<folder>.*)" named "(?P<name>.*)"')
def step_impl(context, folder, name):
    # Create a copy of the folder in a temporary folder and store the path in the context
    current_dir = os.path.dirname(os.path.abspath(__file__))
    original_folder = os.path.join(current_dir, folder)
    temp_dir = tempfile.mkdtemp()
    target_folder = os.path.join(temp_dir, name)
    shutil.copytree(original_folder, target_folder)
    add_named_attribute_to_context(context, name, target_folder)


@given(u'I have the (file|script) "(?P<file>.*)" as "(?P<name>.*)"')
def step_impl(context, file_or_script, file, name):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    absolute_path = os.path.join(current_dir, file)
    add_named_attribute_to_context(context, name, absolute_path)
    # Extract the folder from the file path and add it to the environment variables PATH
    folder = os.path.dirname(absolute_path)
    os.environ['PATH'] = f"{folder}:{os.environ['PATH']}"




@when(u'I call the (python script|script) "(?P<script>.*)" with the following arguments using the folder "(?P<folder>.*)" as the current directory')
def step_when_call_python_script(context, script_or_python_script, script, folder):
    script_path = context.named_attributes[script]

    if script_or_python_script == 'python script':
        command = f"python {script_path}"
    else:
        command = f"{script_path}"

    for row in context.table:
        arg_name = row['arg_name']
        arg_value = row['arg_value']
        if arg_value in context.named_attributes:
            arg_value = context.named_attributes[arg_value]
        if arg_value and arg_name:
            command += f" {arg_name} {arg_value}"
        if arg_value and not arg_name:
            command += f" {arg_value}"
        else:
            command += f" {arg_name}"

    # Alter the command to pass the path environment variable
    command = f"PATH={os.environ['PATH']} {command}"
    context.output = subprocess.check_output(command, cwd=context.named_attributes[folder], shell=True).decode()


@then(u'the output should contain this (?P<list>.*) of files from the folder "(?P<folder>.*)"')
def step_then_output_contains_list(context, list=None, folder=None):
    if not list:
        assert len(context.output.strip()) == 0
        return
    matching_files = context.output.strip().split('\n')
    files = list.split(', ') if list else []
    for file in files:
        file = os.path.join(context.named_attributes[folder], file)
        assert file in matching_files


@then(u'the output should not contain this (?P<not_list>.*) of files from the folder "(?P<folder>.*)"')
def step_then_output_not_contains_list(context, not_list=None, folder=None):
    if not not_list:
        return
    files = not_list.split(', ')
    for file in files:
        file = os.path.join(context.named_attributes[folder], file)
        assert file not in context.output


@then(u'the entries in the file "(?P<file>.*)" should contain the old public key (?P<old_public_key>.*) and the new public key (?P<new_public_key>.*)')
def step_then_sops_config_contains_new_key(context, file, old_public_key, new_public_key):
    with open(context.named_attributes[file], 'r', encoding='utf-8') as file:
        sops_config = yaml.safe_load(file)

    # Get the creation rules from the sops configuration
    creation_rules = sops_config.get('creation_rules', [])

    # For each rule, check if the old public key is in the 'age' field
    for rule in creation_rules:
        if old_public_key in rule['age']:
            # If the old public key is in the 'age' field, assert that the new public key is also there
            assert new_public_key in rule['age'], f"New public key {new_public_key} not found in rule: {rule}"

@then(u'the output should contain "(?P<message>.*)" for each file in this list of files from the folder "(?P<folder>.*)"')
def step_then_output_contains_decrypted(context, message, folder):
    lines = context.output.strip().split('\n')
    assert len(lines) == len(context.table.rows), f"Number of lines in output is different from number of files"
    for row in context.table:
        file = os.path.join(context.named_attributes[folder], row['file'])
        found = False
        for line in lines:
            if message in line and file in line:
                found = True
                break
        assert found, f"Message {message} not found in file {file} output"
