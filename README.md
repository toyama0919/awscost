# awscost




[![PyPI version](https://badge.fury.io/py/awscost.svg)](https://badge.fury.io/py/awscost)
[![Build Status](https://secure.travis-ci.org/toyama0919/awscost.png?branch=master)](http://travis-ci.org/toyama0919/awscost)

Command Line utility for cost of aws.

Support python3 only. (use boto3)

## Settings

aws auth support following.

* environment
* profile
* instance profile

## Examples

### list-ce

```sh
Usage: awscost list-ce [OPTIONS]

  list cost explorer

Options:
  -g, --granularity [DAILY|MONTHLY]
                                  granularity. (default: MONTHLY)
  -p, --point INTEGER             number of data point. (default: 10)
  --start TEXT                    range of start day. default is 10 month ago.
  --end TEXT                      range of end day. default is now.
  -t, --tablefmt TEXT             tabulate format. (default: simple)
  --group-by [AZ|INSTANCE_TYPE|LINKED_ACCOUNT|OPERATION|PURCHASE_TYPE|SERVICE|USAGE_TYPE|PLATFORM|TENANCY|RECORD_TYPE|LEGAL_ENTITY_NAME|DEPLOYMENT_OPTION|DATABASE_ENGINE|CACHE_ENGINE|INSTANCE_TYPE_FAMILY|REGION|BILLING_ENTITY|RESERVATION_ID|SAVINGS_PLANS_TYPE|SAVINGS_PLAN_ARN|OPERATING_SYSTEM]
                                  group by keys. (default: ["SERVICE"])
  --filter LOADS                  filter of dimensions. default is no filter.
  --help                          Show this message and exit.
```

### show cost

show cost latest 5 months.

```sh
$ awscost list-ce -g MONTHLY -p 5
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

```sh
$ awscost list-ce -g DAILY -p 3 --group-by SERVICE --group-by OPERATION
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

## Installation

```sh
pip install awscost
```

## Contributing

1. Fork it
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create new [Pull Request](../../pull/new/master)

## Information

* [Homepage](https://github.com/toyama0919/awscost)
* [Issues](https://github.com/toyama0919/awscost/issues)
* [Documentation](http://rubydoc.info/gems/awscost/frames)
* [Email](mailto:toyama0919@gmail.com)
