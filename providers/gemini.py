from google import genai
class Gemini():
    def __init__(self, api_key):
        stauts, msg, client = self.validate(api_key)["stauts"],self.validate(api_key)["msg"], self.validate(api_key)["client"]
        self._validation = stauts
        self._client = client
        self._msg = msg

    @property
    def validation(self):
        return self._validation

    @property
    def msg(self):
        return self._msg
    
    @property
    def client(self):
        return self._client

    def validate(self, api_key: str) -> dict:
        stauts = False
        try:
            api_key = api_key.strip()
            client = genai.Client(api_key=api_key)
            models = client.models.list()
            stauts = True
            msg = "Valid api key"
            return{"stauts": stauts, "msg": msg, "client": client}
        except Exception as e:
            err_str = str(e)
            if "API_KEY_INVALID" in err_str:
                msg = "Your API key is incorrect or not activated!"
            else:
                msg = "An error occurred while connecting to the server."

            return {"stauts": stauts, "msg": msg, "client": None}
            