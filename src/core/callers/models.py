class BaseCaller:
    def __init__(self, system_message, model, max_tokens=16000):
        self.system_message = system_message
        self.model = model
        self.max_tokens = max_tokens

    def call(self, messages):  # noqa: ARG002
        raise NotImplementedError
