# AWS IAM Access Key Rotation Automation

## Overview

This project automates the monitoring and rotation of AWS IAM user access keys using AWS Lambda, IAM, Secrets Manager, and SNS.

The solution scans all IAM users in an AWS account and identifies users who:

* Have no access keys.
* Have inactive access keys.
* Have active access keys older than 90 days.
* Have more than one access key.

When a rotation condition is detected, the Lambda function automatically creates a new access key, securely stores it in AWS Secrets Manager, and sends a notification through Amazon SNS.

To avoid application outages, the solution does **not** automatically delete existing access keys. Instead, it notifies administrators to review and remove old keys after applications have been updated.

---

## Architecture

```text
+------------------+
| EventBridge Rule |
| (Scheduled Run)  |
+--------+---------+
         |
         v
+------------------+
| AWS Lambda       |
| Key Rotation     |
+--------+---------+
         |
         +-------------------+
         |                   |
         v                   v
+----------------+   +----------------+
| IAM            |   | SecretsManager |
| List Users     |   | Store New Keys |
+----------------+   +----------------+
         |
         v
+----------------+
| Amazon SNS     |
| Notifications  |
+----------------+
```

---

## Features

* Enumerates all IAM users using pagination.
* Detects users with no access keys.
* Detects inactive access keys.
* Detects access keys older than 90 days.
* Creates replacement access keys automatically.
* Stores new credentials securely in AWS Secrets Manager.
* Sends SNS notifications for key rotation events.
* Alerts administrators when users have multiple access keys.
* Avoids automatic deletion of existing keys to prevent service disruption.

---

## Workflow

### Scenario 1: User Has No Access Keys

1. Lambda detects the user has no access keys.
2. A new access key is generated.
3. Credentials are stored in Secrets Manager.
4. SNS notification is sent.

### Scenario 2: Access Key Older Than 90 Days

1. Lambda detects an outdated key.
2. A new access key is generated.
3. Credentials are stored in Secrets Manager.
4. SNS notification is sent.
5. Administrator reviews and removes the old key after updating applications.

### Scenario 3: Inactive Access Key

1. Lambda detects an inactive key.
2. A new access key is generated.
3. Credentials are stored in Secrets Manager.
4. SNS notification is sent.

### Scenario 4: Multiple Access Keys

1. Lambda detects more than one access key.
2. No automatic action is performed.
3. SNS notification is sent requesting manual review.

---

## AWS Services Used

* AWS Lambda
* AWS IAM
* AWS Secrets Manager
* Amazon SNS
* Amazon EventBridge

---

## Required IAM Permissions
### For Lambda
The Lambda execution role requires permissions similar to:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iam:ListUsers",
        "iam:ListAccessKeys",
        "iam:CreateAccessKey"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:CreateSecret",
        "secretsmanager:PutSecretValue"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "sns:Publish"
      ],
      "Resource": "*"
    }
  ]
}
```

### For user
This will allow only the intended user can access the secret using tag
{
  "Effect": "Allow",
  "Action": "secretsmanager:GetSecretValue",
  "Resource": "*",
  "Condition": {
    "StringEquals": {
      "aws:ResourceTag/Owner": "${aws:PrincipalTag/Owner}"
    }
  }
}
---

## Configuration

Update the SNS Topic ARN in the Lambda function:

```python
TOPIC_ARN = "arn:aws:sns:region:account-id:topic-name"
```

Configure an EventBridge schedule to invoke the Lambda function periodically.

Recommended schedule:

```text
rate(1 day)
```

---

## Secrets Manager Structure

Example secret stored in Secrets Manager:

```json
{
  "UserName": "developer-user",
  "AccessKeyId": "AKIAxxxxxxxxxxxxxxxx",
  "SecretAccessKey": "xxxxxxxxxxxxxxxxxxxxxxxx",
  "CreatedAt": "2026-06-07T10:00:00Z"
}
```

---

## Security Considerations

* Credentials are stored securely in AWS Secrets Manager.
* Existing access keys are not automatically deleted.
* Human approval is required before removing old credentials.
* Notifications provide visibility into key rotation events.
* Supports AWS IAM access key rotation best practices.

---

## Future Enhancements

* Automatic disabling of old access keys after a grace period.
* DynamoDB tracking to prevent duplicate notifications.
* CloudWatch dashboard for key rotation metrics.
* Security Hub integration.
* AWS Config compliance checks.
* Automated ticket creation in Jira or ServiceNow.
* Slack or Microsoft Teams notifications.

---

## Author

AWS Security Automation Project

Focus Areas:

* IAM Security
* Secrets Management
* Credential Rotation
* Security Operations Automation
* AWS Serverless Security
