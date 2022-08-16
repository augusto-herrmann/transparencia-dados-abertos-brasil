# Automatic link verification script

This script crawls candidate URLs for municipalities websites and
checks if they are active and likely to be the city hall or
city council portals.

## Usage

1. Create a Pyton virtual environment. This is not required, but it is
   recommended.
2. Install the dependencies. From the tools directory:
   ```bash
   pip install -e .
   ```
3. Run the script:
   ```bash
   python auto_verify_links.py input_file.csv output_file.csv -q quantity -p processes
   ```
   
   For more information run:
   ```bash
   python auto_verify_links.py --help
   ```

Note: Python 3 is required for this script. Tested on 3.8.10.
