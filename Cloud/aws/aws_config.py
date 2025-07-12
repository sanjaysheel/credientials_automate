def process_aws_credentials(profile, region, mfa_arn, token_code, base_dir=None):
    return {
        "status": "pending",
        "message": "AWS MFA support coming soon.",
        "profile": profile,
        "region": region,
        "mfa_arn": mfa_arn,
        "token_code": token_code
    }
