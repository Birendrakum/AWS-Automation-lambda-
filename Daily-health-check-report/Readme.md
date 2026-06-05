# AWS Highly Available Web Application Infrastructure

## Overview

This project provisions a highly available web application infrastructure on AWS using CloudFormation.

The stack includes:

- Amazon VPC
- Public and Private Subnets across multiple Availability Zones
- Internet Gateway
- NAT Gateway
- Route Tables and Associations
- Application Load Balancer (ALB)
- EC2 Launch Template
- Auto Scaling Group (ASG)
- CloudWatch Monitoring
- AWS Lambda Reporting Function
- Amazon S3 Report Storage
- Amazon EventBridge Scheduler

---

## Architecture

```text
                     Internet
                         |
                         v
              +-------------------+
              | Application Load  |
              |     Balancer      |
              +-------------------+
                         |
                         v
       +--------------------------------------+
       |        Auto Scaling Group            |
       |                                      |
       |   EC2 Instances in Private Subnets   |
       +--------------------------------------+
                         |
        +----------------+----------------+
        |                                 |
        v                                 v
 CloudWatch Metrics               Lambda Reporting
                                          |
                                          v
                                     S3 Bucket

EventBridge
     |
     v
 Lambda (Hourly Execution)
```

---

## Infrastructure Components

### Networking

#### VPC

| Property | Value |
|-----------|---------|
| CIDR Block | `192.168.10.0/24` |

### Public Subnets

| Name | CIDR | Availability Zone |
|--------|--------|--------|
| PublicA | 192.168.10.64/26 | us-east-1a |
| PublicB | 192.168.10.128/26 | us-east-1b |

### Private Subnets

| Name | CIDR | Availability Zone |
|--------|--------|--------|
| PrivateA | 192.168.10.0/26 | us-east-1a |
| PrivateB | 192.168.10.192/26 | us-east-1b |

---

## Internet Connectivity

### Internet Gateway

Provides internet access for public resources.

### NAT Gateway

Allows private instances to:

- Download software updates
- Access package repositories
- Reach external services securely

without exposing them directly to the internet.

---

## Security Groups

### Load Balancer Security Group

Allows inbound traffic:

```text
TCP 80 from 0.0.0.0/0
```

### EC2 Security Group

Allows inbound traffic only from the ALB:

```text
TCP 80 from ALB Security Group
```

This prevents direct internet access to EC2 instances.

---

## Application Load Balancer

### Features

- Internet-facing
- HTTP Listener on Port 80
- Health Checks
- Cross-AZ Load Balancing
- Integrated with Auto Scaling Group

---

## Launch Template

### Instance Configuration

| Property | Value |
|-----------|---------|
| Instance Type | t2.micro |
| Operating System | Ubuntu |
| Web Server | Apache2 |

### Bootstrap Actions

The UserData script:

1. Updates the operating system
2. Installs Apache2
3. Creates a sample web page
4. Starts the Apache service
5. Enables Apache at boot

---

## Auto Scaling Group

### Configuration

| Property | Value |
|-----------|---------|
| Minimum Capacity | 2 |
| Maximum Capacity | 4 |
| Availability Zones | us-east-1a, us-east-1b |

### Benefits

- High Availability
- Fault Tolerance
- Automatic Scaling
- Multi-AZ Deployment

---

## CloudWatch Monitoring

The infrastructure includes CloudWatch alarms and scaling policies to monitor application health and capacity.

### Metrics Monitored

- CPU Utilization
- Instance Health
- Scaling Activities

---

## Lambda Reporting Solution

### Purpose

The Lambda function collects Auto Scaling Group information and generates operational reports.

### Report Contents

- Report Timestamp
- Auto Scaling Group Name
- Desired Capacity
- Minimum Size
- Maximum Size
- Number of Instances
- Instance Details
  - Instance ID
  - Lifecycle State
  - Health Status
  - CPU Utilization
- Scaling Activities

---

## Amazon S3 Report Storage

Reports are stored in a dedicated S3 bucket.

### Example Report Location

```text
s3://<bucket-name>/asg-reports/
```

### Example Report File

```text
asg_report_20260605_140000.json
```

---

## EventBridge Scheduler

### Schedule

```text
cron(0 * * * ? *)
```

### Execution Times

```text
00:00
01:00
02:00
03:00
...
23:00
```

### Workflow

```text
EventBridge
      |
      v
Lambda
      |
      v
Collect ASG Information
      |
      v
Store Report in S3
```

---

## IAM Permissions

The Lambda execution role includes permissions for:

### CloudWatch

```text
cloudwatch:GetMetricStatistics
```

### Auto Scaling

```text
autoscaling:DescribeAutoScalingGroups
autoscaling:DescribeScalingActivities
```

### Amazon S3

```text
s3:PutObject
s3:ListBucket
```

---

## Deployment

### Validate CloudFormation Template

```bash
aws cloudformation validate-template \
  --template-body file://Infrastructure.yml
```

### Create Stack

```bash
aws cloudformation create-stack \
  --stack-name my-webapp-stack \
  --template-body file://Infrastructure.yml \
  --capabilities CAPABILITY_NAMED_IAM
```

### Monitor Stack Status

```bash
aws cloudformation describe-stacks \
  --stack-name my-webapp-stack
```

---

## Outputs

The CloudFormation stack provides the following outputs:

### LoadBalancerDNS

DNS name of the Application Load Balancer.

### BucketName

Amazon S3 bucket used for report storage.

### LambdaName

Lambda function name.

### ASGName

Auto Scaling Group name.

---

## Testing

### Access the Application

Open the ALB DNS name in a browser:

```text
http://<LoadBalancerDNS>
```

Expected response:

```html
Hello from ASG
```

### Verify Reports

Navigate to:

```text
S3 Bucket
 └── asg-reports/
```

Verify that hourly JSON reports are being generated.

---

## Future Enhancements

- HTTPS using AWS Certificate Manager (ACM)
- AWS WAF Integration
- Route 53 DNS Configuration
- CloudWatch Dashboards
- SNS Notifications
- AWS CodePipeline Integration
- Containerization with Amazon EKS or ECS
- Centralized Logging with CloudWatch Logs

---

## AWS Resources Created

- 1 VPC
- 4 Subnets
- 2 Route Tables
- 1 Internet Gateway
- 1 NAT Gateway
- 2 Security Groups
- 1 Application Load Balancer
- 1 Target Group
- 1 Listener
- 1 Launch Template
- 1 Auto Scaling Group
- CloudWatch Monitoring Resources
- 1 IAM Role
- 1 Lambda Function
- 1 Amazon S3 Bucket
- 1 EventBridge Rule
- 1 Lambda Permission

---

## Author

Infrastructure deployed and managed using AWS CloudFormation.

---
