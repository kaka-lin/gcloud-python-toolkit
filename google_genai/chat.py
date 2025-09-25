import os

from dotenv import load_dotenv
from google import genai
from google.genai import types


class GeminiService:
    """
    Service for various tasks via Google Gemini API,
    including ASR, translation, dialogue, Q&A, etc.
    """
    def __init__(self, model_name: str = "gemini-2.5-flash", gemini_api_key: str = ""):
        self.model_name = model_name

        # Get service configurations
        self.temperature = 0.0
        self.max_output_tokens = 100
        self.timeout = 5

        # Get Gemini API key from config or environment variable
        self.api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Gemini API key is not set. Please provide it in the config "
                "or as an environment variable."
            )

        # Initialize Gemini client
        self.client = genai.Client(api_key=self.api_key)

    def process(self, input_text: str) -> str:
        """使用 Google Gemini API 處理輸入"""
        # ==================================================================
        #                        FOR ERROR TESTING
        # ==================================================================
        # Instructions: Uncomment the following lines to simulate
        #               a specific Gemini API error for testing purposes.
        # ------------------------------------------------------------------

        # 1. Simulate a Rate Limit Error (HTTP 429)
        # from google.api_core import exceptions
        # raise exceptions.ResourceExhausted(
        #     "Quota exceeded for aiplatform.googleapis.com/generate_content."
        # )
        # ==================================================================

        # ==================================================================
        #                        FOR THINKING CONFIG
        # ==================================================================
        # 2.5 Flash 和 Pro 模型預設啟用「思考」功能，以提升品質，但可能會導致執行時間拉長，並增加符記用量。
        # 使用 2.5 Flash 時，您可以將思考預算設為零，藉此停用思考功能。
        #
        # Turn off thinking:
        # thinking_config=types.ThinkingConfig(thinking_budget=0)
        #
        # Turn on dynamic thinking:
        # thinking_config=types.ThinkingConfig(thinking_budget=-1)
        # ==================================================================

        # Create a chat session, put system prompt in the session
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=input_text,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0),  # Disables thinking
                system_instruction="You are a helpful assistant.",
                temperature=self.temperature,
                max_output_tokens=self.max_output_tokens,
            ),
        )

        # The response structure has also changed.
        # It's better to access the text via response.text
        return response.text.strip()


if __name__ == "__main__":
    # 載入 .env 內容到環境變數，並強制更新
    if not load_dotenv(override=True):
        print("警告：.env 檔案不存在或解析失敗，請確認它位於專案根目錄。")

    gemini_agent = GeminiService()
    input_text = "你好，簡介一下你自己"
    response = gemini_agent.process(input_text)
    print("問題: ", input_text)
    print("回答: ", response)
