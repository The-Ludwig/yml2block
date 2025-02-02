"""Dispatch entry to specialized lint rules."""
from yml2block import rules


def validate_yaml(data, lint_conf, verbose):
    """Check if the given yaml file is valid.

    Underlying checks will return lists of LintViolations if they don't.
    """
    violations = validate_keywords(data.keys(), lint_conf, verbose)
    longest_row = 0
    for kw, content in data.items():
        block_row_max, entry_violations = validate_entry(
            data[kw], kw, lint_conf, verbose
        )
        violations.extend(entry_violations)
        longest_row = max(longest_row, block_row_max)

    return longest_row, violations


def validate_keywords(keywords, lint_conf, verbose):
    """Assure that the top-level keywords of the YAML file are well-behaved."""
    if verbose == 1:
        print("Validating top-level keywords:", end=" ")
    elif verbose >= 2:
        print(f"Validating top-level keywords:\n{keywords}")

    violations = []
    for lint in [
        rules.keywords_valid,
        rules.keywords_unique,
    ]:
        if verbose >= 2:
            print(f"Running lint: {lint.__name__}")

        lint = lint_conf.get(lint)
        violations.extend(lint(keywords))

    if verbose and len(violations) == 0:
        print("SUCCESS!" if verbose == 1 else "SUCCESS!\n")
    if violations:
        print("FAILURE! Detected violations:")
        print("\n".join([str(v) for v in violations]))
        return violations
    else:
        return []


def validate_entry(yaml_chunk, tsv_keyword, lint_conf, verbose):
    """Validate a record, based on its type.

    Perform second level list item lints.
    Return a list of errors if violations are detected.
    """
    if verbose == 1:
        print(f"Validating entries for {tsv_keyword}:", end=" ")
    elif verbose >= 2:
        print(f"Validating entries for {tsv_keyword}:\n{yaml_chunk}")

    violations = []
    for lint in (rules.block_is_list,):
        lint = lint_conf.get(lint)
        violations.extend(lint(yaml_chunk))

    longest_row = 0

    for lint in (rules.unique_names,):
        lint = lint_conf.get(lint)
        violations.extend(lint(yaml_chunk, tsv_keyword))

    for item in yaml_chunk:
        for lint in (
            rules.keys_valid,
            rules.required_keys_present,
            rules.no_substructures,
            rules.no_trailing_spaces,
        ):
            if verbose >= 2:
                print(f"Running lint: {lint.__name__}")

            lint = lint_conf.get(lint)
            violations.extend(lint(item, tsv_keyword))

        # Compute the highest number of columns in the block
        row_length = (
            len(item.keys()) if tsv_keyword == "metadataBlock" else len(item.keys()) + 1
        )
        longest_row = max(longest_row, row_length)

    if verbose and len(violations) == 0:
        print("SUCCESS!" if verbose == 1 else "SUCCESS!\n")
    if verbose and violations:
        print("FAILURE! Detected violations:")
        print("\n".join([str(v) for v in violations]))

    return longest_row, violations
