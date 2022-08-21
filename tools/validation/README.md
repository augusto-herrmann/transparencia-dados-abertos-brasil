# Link verification scripts

These scripts crawl candidate URLs for municipalities websites and
checks if they are active and likely to be the city hall or
city council portals.

The manual version opens the website on a new browser tab so the user
can check if the site does indeed correspond to the city portal, and
what kind of portal it is.

## Usage

1. Create a Pyton virtual environment. This is not required, but it is
   recommended.
2. Install the dependencies. From the tools directory:
   ```bash
   pip install -e .
   ```
3. Run the script:
   ```bash
   python auto_verify_links.py input_file.csv output_file.csv -q {quantity} -p {processes}
   ```

   Where `{quantity}` is the maximum quantity of links to check and
   `{processes}` is the number of processes to use in parallel.

   For more information run:
   ```bash
   python auto_verify_links.py --help
   ```

   or
   ```bash
   python manually_verify_links.py --help
   ```

Note: Python 3 is required for this script.
