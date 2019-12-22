# Automatic link verification script

This script crawls candidate URLs for municipalities websites and
checks if they are active and likely to be the city hall or
city council portals.

## Usage

1. Create a Pyton virtual environment. This is not required, but it is
   recommended.
2. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the script:
   ```
   python auto-verify-links.py input_file.csv output_file.csv -q quantity -p processes
   ```
   
   For more information run:
   ```
   python auto-verify-links.py --help
   ```

Note: Python 3 is required for this script. Tested on 3.6.9. Python 2 is not
supported.

