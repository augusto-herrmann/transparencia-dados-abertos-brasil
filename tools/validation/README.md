# Link verification scripts

These scripts crawl candidate URLs for municipalities websites and
checks if they are active and likely to be the city hall or
city council portals.

The manual version opens the website on a new browser tab so the user
can check if the site does indeed correspond to the city portal, and
what kind of portal it is.

## Usage

1. Create a Python virtual environment. This is not required, but it is
   recommended.
2. Install the dependencies. From the tools directory:
   ```bash
   pip install -e .
   ```
3. Run the script:
   ```bash
   python auto_verify_links.py input_file.csv output_folder -q {quantity} -p {processes}
   ```

   Where `{quantity}` is the maximum quantity of links to check and
   `{processes}` is the number of processes to use in parallel.

   For example, to automatically crawl 100 candidate links in the default
   folder, using 10 parallel processes, use:

   ```bash
   python auto_verify_links.py ../../data/unverified/municipality-website-candidate-links.csv ../../data/valid/ -q 100 -p 10
   ```

   For more information run:
   ```bash
   python auto_verify_links.py --help
   ```

   or
   ```bash
   python manually_verify_links.py --help
   ```

Note: Python 3 is required for this script.
