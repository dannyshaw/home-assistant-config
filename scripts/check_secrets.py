import yaml


def get_yaml_keys_set(my_file):
    keys = set()
    with open(my_file, 'r') as fp:
        docs = yaml.safe_load_all(fp)
        for doc in docs:
            for key, _ in doc.items():
                keys.add(key)
    return keys


if __name__ == '__main__':
    a = get_yaml_keys_set('./secrets.yaml')
    b = get_yaml_keys_set('./secrets_ci.yaml')

    secrets_unique = a - b
    secrets_ci_unique = b - a

    if secrets_unique:
        out = "\n".join(sorted(secrets_unique))
        print(f'Keys in secrets.yaml but not in secrets_ci.yaml: \n{out}\n')

    if secrets_ci_unique:
        out = "\n".join(sorted(secrets_ci_unique))
        print(f'Keys in secrets_ci.yaml but not in secrets.yaml: \n{out}')

    if secrets_unique or secrets_ci_unique:
        exit(1)
