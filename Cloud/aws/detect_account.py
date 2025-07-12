import boto3

def get_identity_info():
    client = boto3.client('sts')
    identity = client.get_caller_identity()
    return {
        "account": identity["Account"],
        "arn": identity["Arn"],
        "user_id": identity["UserId"]
    }
