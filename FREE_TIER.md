# AWS cost-safety notes

CareerAgent AI is configured as a low-usage portfolio/demo stack. Its default AI provider is `mock`, which makes no paid model calls.

## Cost-aware defaults

- One Python Lambda function.
- API Gateway HTTP API rather than a continuously running server.
- DynamoDB `PAY_PER_REQUEST`, so there is no provisioned always-on throughput in the template.
- Private S3 CV bucket with a 7-day lifecycle rule.
- No NAT Gateway, EC2, RDS, OpenSearch, ECS cluster or Kubernetes cluster.
- Amazon Bedrock is optional and disabled by default.
- Local Ollama can provide real LLM output without a model API charge when running on your own computer.

## Important

AWS offers, free allowances, credits and prices vary by account, region and date. This project minimizes resources but cannot guarantee a $0 AWS bill.

Before deploying:
1. Review the AWS pricing/free-offer pages for your account and region.
2. Create an AWS Budget / billing alert.
3. Deploy with `AiProvider=mock` first.
4. Do not enable Bedrock unless you intend to use it.
5. Delete the stack when you are finished demonstrating it.

## Delete the stack

```bash
./scripts/destroy-aws.sh
```
