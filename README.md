# awscost

[![PyPI version](https://badge.fury.io/py/awscost.svg)](https://badge.fury.io/py/awscost)
[![Build Status](https://secure.travis-ci.org/toyama0919/awscost.png?branch=master)](http://travis-ci.org/toyama0919/awscost)

Command Line utility for Provides aws cost very easy to see.

Supports python 3.6 or later.

## Install

```bash
$ pip install awscost
```

## Examples

### show cost

show cost latest 5 months.

```bash
$ awscost
key                                       2019-07    2019-08    2019-09    2019-10    2019-11    2019-12
--------------------------------------  ---------  ---------  ---------  ---------  ---------  ---------
Total                                      348.34      97.4       98.46     106.47      67.25       7.84
EC2 - Other                                 34.28      34.28      33.2       34.28      33.63       3.01
Amazon Elastic Compute Cloud - Compute      17.11      17.11      16.56      17.11      17.13       1.47
AWS Cost Explorer                                                                        0.56       1.44
Tax                                         25.8        7.22       7.27       9.72       6.12       0.69
AWS CloudTrail                               3.29       3.21       4.15       5.57       4.44       0.61
AWS Key Management Service                   0          0          2.8        4          4          0.35
AmazonCloudWatch                             1.5        0.01       0          0          0.88       0.11
Amazon Route 53                              0.1        0.1        0.1        0.1        0.1        0.1
Amazon Simple Storage Service                0.25       0.24       0.27       0.45       0.4        0.05
AWS Lambda                                   0          0          0          0          0          0
Amazon DynamoDB                              0          0          0          0          0
Amazon Elastic File System                   0          0          0          0          0          0
Amazon SageMaker                           266         35.22      34.11      35.22       0
Amazon Simple Notification Service           0          0                                0
Amazon Polly                                                                  0
Amazon Simple Queue Service                                                              0
```

show cost latest 3 days, group by SERVICE and operation.

```bash
$ awscost -g DAILY -p 3 -d SERVICE -d OPERATION
key                                                             2019-12-01    2019-12-02    2019-12-03
------------------------------------------------------------  ------------  ------------  ------------
Total                                                                 2.87          2.1           2.87
GetCostAndUsage,AWS Cost Explorer                                                   0.02          1.42
NatGateway,EC2 - Other                                                1.08          1.08          0.77
RunInstances,Amazon Elastic Compute Cloud - Compute                   0.55          0.55          0.37
None,AWS CloudTrail                                                   0.22          0.22          0.17
Unknown,AWS Key Management Service                                    0.13          0.13          0.09
Unknown,AmazonCloudWatch                                              0.04          0.04          0.03
CreateVolume-Gp2,EC2 - Other                                          0.03          0.03          0.01
PutObject,Amazon Simple Storage Service                               0.02          0.02          0.01
NoOperation,Tax                                                       0.25
...
```

### support dimensions

* AZ
* INSTANCE_TYPE
* LINKED_ACCOUNT
* OPERATION
* PURCHASE_TYPE
* SERVICE
* USAGE_TYPE
* PLATFORM
* TENANCY
* RECORD_TYPE
* LEGAL_ENTITY_NAME
* DEPLOYMENT_OPTION
* DATABASE_ENGINE
* CACHE_ENGINE
* INSTANCE_TYPE_FAMILY
* REGION
* BILLING_ENTITY
* RESERVATION_ID
* SAVINGS_PLANS_TYPE
* SAVINGS_PLAN_ARN
* OPERATING_SYSTEM

see. https://docs.aws.amazon.com/aws-cost-management/latest/APIReference/API_GetDimensionValues.html

### support filter

```bash
awscost --filter '{
  "Not": {
    "Dimensions": {
      "Key": "RECORD_TYPE",
      "Values": ["Credit", "Refund", "Upfront"]
    }
  }
}'
```

## config file($HOME/.awscost)

```yaml
default:
  metrics: AmortizedCost
  filter:
    Dimensions:
      Key: RECORD_TYPE
      Values:
        - Usage
        - Tax

discount:
  filter:
    Dimensions:
      Key: RECORD_TYPE
      Values:
        - Credit
        - Refund
        - Upfront
```

You can exec command as below.

```bash
$ awscost --profile discount
```

## Various format(-t option)

example, use -t tsv.

default is simple.

```bash
$ awscost -d SERVICE -d OPERATION -t tsv
key                                                             01-24   01-25   01-26   01-27   01-28   01-29   01-30   01-31   02-01   02-02
Total                                                            2       2       2       2       2.02    2.01    2.01    2.01    2.5     1.67
EC2 - Other,NatGateway                                           1.08    1.08    1.08    1.08    1.08    1.08    1.08    1.08    1.08    0.9
Amazon Elastic Compute Cloud - Compute,RunInstances              0.55    0.55    0.55    0.55    0.55    0.55    0.55    0.55    0.55    0.46
...
```

### support format
- simple(default)
- plain
- github
- grid
- fancy_grid
- pipe
- orgtbl
- jira
- presto
- psql
- rst
- mediawiki
- moinmoin
- youtrack
- html
- latex
- latex_raw
- latex_booktabs
- textile
- tsv

## Settings

aws auth support following.

* environment variables
* profile(use --aws-profile option.)
* instance profile



## Python API

```py
from awscost.cost_explorer import CostExplorer
from dateutil.relativedelta import relativedelta
from datetime import datetime

start = (datetime.today() - relativedelta(months=3)).strftime("%Y-%m-01")
end = datetime.today().strftime("%Y-%m-01")

cost_explorer = CostExplorer(
    "MONTHLY", start, end, dimensions=["SERVICE"], metrics="UnblendedCost"
).get_cost_and_usage_total_and_group_by()

# return dict data. 
cost_explorer # =>
# {   'AWS CloudTrail': {'2019-11': 4.44, '2019-12': 6.17, '2020-01': 4.38},
#     'AWS Lambda': {'2019-11': 0.0, '2019-12': 0.0, '2020-01': 0.0},
# ...
#     'Total': {'2019-11': 67.15, '2019-12': 72.22, '2020-01': 68.11}}

```

### matplotlib

```py
...

import matplotlib.pyplot as plt

plt.figure(figsize=(25, 15), dpi=100)
plt.xlabel('month', fontsize=16)
plt.ylabel('$', fontsize=16)
plt.grid(True)
for i, (service_name, v) in enumerate(cost_explorer.items()):
    left = list(v.keys())
    height = list(v.values())
    plt.plot(left, height, linewidth=2, label=service_name, marker='o')
plt.legend(loc='best', fontsize=15, numpoints=5)

plt.show()

```

## iam policy

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "xxxxxxxxx",
            "Effect": "Allow",
            "Action": [
                "ce:GetCostAndUsage"
            ],
            "Resource": "*"
        }
    ]
}
```

## CI

### install test package

```bash
$ ./scripts/ci.sh install-test
```

### test

```bash
$ ./scripts/ci.sh run-test
```

flake8 and black and pytest.

### release pypi

```bash
$ ./scripts/ci.sh release
```

git tag and pypi release.
