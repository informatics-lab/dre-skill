from intent_processing.lambda_fn import go

def start(event, context):
	return go(event, context)