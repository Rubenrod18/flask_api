import json
import re

with open('package.json', encoding='utf-8') as f:
    version = json.load(f)['version']

with open('src/pyproject.toml', encoding='utf-8') as f:
    toml_content = f.read()

# Replace the version in the [project] section while preserving formatting
# Using a lambda function to avoid group reference confusion
toml_content = re.sub(
    r'^(version\s*=\s*")[^"]+(")',
    lambda match: f'{match.group(1)}{version}{match.group(2)}',
    toml_content,
    flags=re.MULTILINE,
)

with open('src/pyproject.toml', 'w', encoding='utf-8') as f:
    f.write(toml_content)

print(f'Version updated to {version} in pyproject.toml')  # noqa
