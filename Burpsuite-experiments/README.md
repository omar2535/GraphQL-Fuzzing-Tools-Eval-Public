# Burpsuite Auto GQL Evaluation setup

1. Setup burp (professional edition)
2. Install [burp-auto-gql](https://github.com/FWDSEC/burp-auto-gql)
3. Run the active scanner
4. Export CSV
5. Run `parse_coverage.py` after saving all CSV files into a directory (seperated by the name) and placing counter-time in the same directory
