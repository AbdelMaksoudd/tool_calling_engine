from google import genai
class Gemini():
    def __init__(self, api_key):
        res = self.validate(api_key)
        self._validation, self._msg, self._client = res["status"], res["msg"], res["client"]
        

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
        status = False
        try:
            api_key = api_key.strip()
            client = genai.Client(api_key=api_key)
            models = [model.name for model in client.models.list()]
            status = True
            msg = "Valid api key"
            return{"status": status, "msg": msg, "client": client}
        except Exception as e:
            err_str = str(e)
            if "API_KEY_INVALID" in err_str:
                msg = "Your API key is incorrect or not activated!"
            else:
                msg = "An error occurred while connecting to the server."

            return {"status": status, "msg": msg, "client": None}
            