# ZAP GraphQL Evaluation

1. Install ZAP GraphQL Add-on
2. Import > Import a GraphQL Schema > Enter Endpoint URL
3. The scanner will automatically trigger.
4. In the history tab, shift+click all the requests and responses
5. Export > Save Messages... > Save as <endpoint_name>-messages.txt
7. Run `python3 parse_coverage.py -f f<endpoint_name>-messages.txt`
8. Use those counts to calculate coveerage
