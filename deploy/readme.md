# boto3-based deployment for datapipes

### toc

- [iam](./iam/readme.md)
- [lambda](./lambda/readme.md)



### set up python packages fro deployment

```
cd lambda
pip install -r requirements.txt -t pkg
```

## todo

- add vpc config for lambda (easy)
- make iam role/policy creation more robust (attach multiple policies, etc)
- delete stuff that's not managed by configuration
- optional deployment for single role, etc versus deploying everything
- determine whether upload to s3 and lambda hookup is better than uploading zip
- deploy all configs to dynamodb
- add functionality for sns, sqs, api gateway
