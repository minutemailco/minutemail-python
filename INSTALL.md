# Installation & Publishing Guide

## Installation Options

### From PyPI (When Published)

```bash
pip install minutemail-sdk
```

### From Git Repository

```bash
pip install git+https://github.com/minutemail/mm-sdk.git
```

### From Local Source (Development)

```bash
# Clone the repository
git clone https://github.com/minutemail/mm-sdk.git
cd mm-sdk

# Install in editable mode
pip install -e .
```

### From Local Source (Production)

```bash
pip install .
```

## Building the Package

### Build Distribution Files

```bash
# Install build tools
pip install build

# Build source distribution and wheel
python -m build

# Output will be in dist/ directory:
# - minutemail_sdk-0.2.0.tar.gz (source distribution)
# - minutemail_sdk-0.2.0-py3-none-any.whl (wheel)
```

## Publishing to PyPI

### Prerequisites

1. Create an account on [PyPI](https://pypi.org/account/register/)
2. Create an API token in your [PyPI account settings](https://pypi.org/manage/account/token/)
3. Install twine:

```bash
pip install twine
```

### Test on TestPyPI First (Recommended)

```bash
# Build the package
python -m build

# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ minutemail-sdk
```

### Publish to PyPI

```bash
# Build the package
python -m build

# Upload to PyPI
python -m twine upload dist/*

# You'll be prompted for:
# - Username: __token__
# - Password: <your-pypi-token>
```

### Using a .pypirc File (Recommended)

Create `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-<your-token-here>

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-<your-test-token-here>
```

Then publish with:

```bash
python -m twine upload dist/*
```

## Version Management

The version is defined in `pyproject.toml`:

```toml
[project]
version = "0.2.0"
```

### Versioning Guidelines

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (X.0.0): Breaking changes
- **MINOR** (0.X.0): New features, backward compatible
- **PATCH** (0.0.X): Bug fixes, backward compatible

### Current Version: 0.2.0

Changes from 0.1.0:
- ✅ Fixed type annotations (expires_in: str → int)
- ✅ Added 4 bulk delete operations
- ✅ Added address query parameter to list_mailboxes()
- ✅ 100% API coverage (23/23 endpoints)

## Verification

After installation, verify the package:

```python
import minutemail
from minutemail import MinuteMailClient

# Check version
print(minutemail.__version__)  # Should print: 0.2.0

# Create client
client = MinuteMailClient(api_key="your-api-key")

# Test a simple call
mailboxes = client.list_mailboxes()
```

## Troubleshooting

### "Package not found" error

Ensure you're using the correct package name:
```bash
pip install minutemail-sdk  # Correct
pip install minutemail      # Wrong
```

### Import errors

Make sure to import from the correct module:
```python
from minutemail import MinuteMailClient  # Correct
from minutemail_sdk import MinuteMailClient  # Wrong
```

### Installation from git requires authentication

If the repository is private:
```bash
pip install git+https://<token>@github.com/minutemail/mm-sdk.git
```

## Uninstalling

```bash
pip uninstall minutemail-sdk
```

## Dependencies

The package has minimal dependencies:
- Python >= 3.9
- requests >= 2.31.0

All dependencies are automatically installed by pip.
