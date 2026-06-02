def generate(bedrock_client, model_id: str, messages: list, system_prompt: str) -> str:
    response = bedrock_client.converse(
        modelId=model_id,
        system=[{'text': system_prompt}],
        messages=messages,
        inferenceConfig={
            "maxTokens": 512,
            "temperature": 0.7
        }
    )
    return response["output"]["message"]["content"][0]["text"]
