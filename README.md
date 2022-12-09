# CloudFormatin


{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": "s3:ListBucket",
            "Resource": "arn:aws:s3:::oai-test-20220917",
            "Condition": {
                "IpAddress": {
                    "aws:SourceIp": "123.226.232.242/32"
                }
            }
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:DeleteObject"
            ],
            "Resource": "arn:aws:s3:::oai-test-20220917/*",
            "Condition": {
                "IpAddress": {
                    "aws:SourceIp": "123.226.232.242/32"
                }
            }
        }
    ]
}
