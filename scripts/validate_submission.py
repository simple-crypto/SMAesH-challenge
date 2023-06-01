
import zipfile

import jsonschema
import tomli

TARGETS = ["A7_d2", "S6_d2"]

def description_schema(targets):
    return {
        "type" : "object",
        "properties" : {
            "team": { "type": "string" },
            "authors" : {
                "type" : "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": { "type": "string" },
                        "email": { "type": "string" },
                        "corresponding": { "type": "boolean" },
                    },
                    "required": ["name"],
                },
            },
            "name" : {"type" : "string"},
            "license" : {"type" : "string"},
            "attacks" : {
                "type" : "object",
                "propertyNames": { "enum": TARGETS, },
                "additionalProperties" : {
                    "type": "object",
                    "properties": { 
                        "n_traces": { "type": "number", "exclusiveMinimum": 0 },
                    },
                    "required": ["n_traces"],
                },
                "minProperties": 1,
            },
        },
        "required": ["team", "authors", "name", "license", "attacks"],
    }


class ValidationError(Exception):
    pass

def validate_submission(f, targets=TARGETS):
    """Validate a submission. f must be a file-like object.

    Returns the description of the submission. Raises a ValidationError if not valid.
    """
    # Check the zip file
    try:
        f = zipfile.ZipFile(f)
    except zipfile.BadZipFile:
        raise ValidationError('Submission file is not a ZIP file.')
    names = f.namelist()
    if not all(n.startswith('submission/') for n in names):
        raise ValidationError('Incorrect zip file content (files not in submission/).')
    setup_fname = 'submission/setup/'
    if not any(n.startswith(setup_fname) for n in names):
        raise ValidationError('Incorrect zip file content (no files in submission/setup directory).')
    toml_fname = 'submission/submission.toml'
    if toml_fname not in names:
        raise ValidationError('Incorrect zip file content (no submission/submission.toml file.).')
    # Get submission.toml content
    toml_file = f.open(toml_fname)
    try:
        description = tomli.load(toml_file)
    except tomli.TOMLDecodeError as e:
        raise ValidationError(f'Incorrect zip file content (submission/submission.toml is not TOML: {e}).') 
    try:
        jsonschema.validate(description, schema=description_schema(targets))
    except jsonschema.ValidationError as e:
        raise ValidationError(f'Bad submission.toml: {e.args[0]}')
    if any(author.get("corresponding") and "email" not in author for author in description["authors"]):
        raise ValidationError("Bad submission.toml: A corresponding does not have email address.")
    if not any(author.get("corresponding") for author in description["authors"]):
        raise ValidationError("Bad submission.toml: There is no corresponding author.")
    return description
    
if __name__ == '__main__':
    import sys
    description = validate_submission(open(sys.argv[1], 'rb'))
    if description['name'].lower().startswith('demo'):
        print('WARNING: Your submission name starts with "demo". Did you forget to change it from the default?', file=sys.stderr)
    print("Validation successful.", file=sys.stderr)
