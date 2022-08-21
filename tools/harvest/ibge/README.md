# IBGE import script

This script imports basic municipality data from IBGE. It is necessary to
import this data before using any of the other sources, as some of them
use this list to search for the existing municipalities.

## Usage

1. Create a Python virtual environment. This is not required, but it is
   recommended.
2. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the script:
   ```
   python ibge-municipalities.py
   ```

Note: Python 3 is required for this script.
