# Evomaster Testing

1. Ensure `evomaster.jar` is installed
2. Run the endpoint's tester (named `<endpoint>_eval.sh`)
2. Parse the results using `parse_coverage.py`

## Example

Running evaluation for EHRI:

1. `/bin/bash ehri_eval.sh`
2. `python parse_coverage.py ehri-5s-src`
3. Number of non-null will be the number of unique endpoints that succeeded
4. Number of faults will be the number of unqiue endpoints with fault
5. Calculate coverage after figuring out total number of endpoints (from schema / API)

## Side notes

To run evomaster manually:

```sh
java -jar evomaster.jar --blackBox true --bbTargetUrl <url> --problemType GRAPHQL --outputFormat JAVA_JUNIT_4 --maxTime 60s
```
