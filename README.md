# AdminProber

**Current Version**: 1.1
**Author**: Trix Cyrus  
**Copyright**: © 2024 Trixsec Org  
**Maintained**: Yes


**AdminProber** is a Python-based tool designed to scan websites for potential admin panels using a wordlist of common admin paths. It can operate with multiple threads to speed up the process and provides an output file with the results.

## Features

- Scan websites for admin panels by testing a list of common admin paths.
- Multi-threaded scanning for faster results.
- Checks for internet connection before starting the scan.
- Checks for updates and allows easy upgrading.
- Saves results to an output file with status codes.
- Customizable admin paths file.
- Colored output for easier readability.

## Requirements

- Python 3.x
- `requests` library
- `termcolor` library
- `urllib3` library

You can install the required dependencies by running:

```bash
pip install -r requirements.txt
```

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/TrixSec/AdminProber.git
   ```

2. Change into the project directory:

   ```bash
   cd AdminProber
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

To start scanning for admin panels on a target website, run the script with the required arguments. Here's an example:

```bash
python adminprober.py --target https://example.com --threads 10 --paths wordlist/admin_paths.txt --output results/admin_results.txt
```

### Command-line arguments:

- `--target` or `-t`: **Required**. The target website URL (e.g., `https://example.com`).
- `--threads` or `-th`: Number of threads to use (default: 5). More threads will speed up the scan.
- `--paths` or `-p`: Path to the file containing admin paths (default: `wordlist/admin_paths.txt`).
- `--output` or `-o`: The file where the results will be saved (default: `results/admin_results.txt`).
- `--check-updates` or `-cu`: Check for the latest version and update if necessary.

## Example

### Running the tool:

```bash
python admin_prober.py --target https://example.com
```

## Update Check

To check if there is a new version of AdminProber available, use the `--check-updates` flag:

```bash
python admin_prober.py --check-updates
```
