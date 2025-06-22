import base64


class Base64Decoder:
    @staticmethod
    def encode_base64(text: str) -> str:
        text_bytes = text.encode('utf-8')
        base64_bytes = base64.b64encode(text_bytes)
        return base64_bytes.decode('utf-8')

    @staticmethod
    def decode_base64(base64_text: str) -> str:
        base64_bytes = base64_text.encode('utf-8')
        text_bytes = base64.b64decode(base64_bytes)
        return text_bytes.decode('utf-8')
