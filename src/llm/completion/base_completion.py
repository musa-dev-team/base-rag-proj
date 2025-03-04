from abc import abstractmethod
import asyncio
import json
from json_repair import repair_json

from src.llm.dtypes import *
from src.duckie_logging.duckie_logger import logging

class LLMCompletion:
    def __init__(self, args: CompletionArgs):
        self.args = args
        self.validate_args()

    def validate_args(self):
        self.args.validate_args()

    async def generate_response(self) -> str | dict:
        max_retries = 3
        backoff = 1
        response = None
        for i in range(max_retries):
            while backoff < 30:
                try:
                    response = await self._generate_response()
                    break
                except Exception as e:
                    if self.is_rate_limited(e):
                        logging.warning(f"Rate limited, backing off for {backoff} seconds")
                        await asyncio.sleep(backoff)
                        backoff *= 2
                    else:
                        raise e
            if response is not None:
                break

        if self.args.json_mode:
            return self.extract_json(response)
        return response

    @abstractmethod
    async def _generate_response(self) -> str: ...

    @staticmethod
    @abstractmethod
    def get_vision_messages(image_data_base64: list) -> list[dict]: ...

    @staticmethod
    @abstractmethod
    def is_rate_limited(e: Exception) -> bool: ...

    @staticmethod
    def extract_json(response: str) -> dict:
        try:
            response = repair_json(response)
            return json.loads(response)
        except Exception as e:
            raise ValueError(f"Failed to extract JSON from response: {e}\nResponse: {response}")
        
if __name__ == "__main__":
    test_cases = [
        """```json
        [{
            "action_type": "COMPLETE",
            "reasoning": "The user has provided sufficient information about their Mattermost and ClamAV Docker setup issue. I can provide a direct response with guidance on configuring inter-container communication to resolve the connectivity problem."
        }]
        ```""",
        """```json
        {
            "action_type": "COMPLETE",
            "reasoning": "The user has provided sufficient information about their Mattermost and ClamAV Docker setup issue. I can provide a direct response with guidance on configuring inter-container communication to resolve the connectivity problem."
        }
        ```""","""
        [{
            "action_type": "COMPLETE",
            "reasoning": "The user has provided sufficient information about their Mattermost and ClamAV Docker setup issue. I can provide a direct response with guidance on configuring inter-container communication to resolve the connectivity problem."
        }]""","""
        {
            "action_type": "COMPLETE",
            "reasoning": "The user has provided sufficient information about their Mattermost and ClamAV Docker setup issue. I can provide a direct response with guidance on configuring inter-container communication to resolve the connectivity problem."
        }""","""```json
{
    "action_type": "FUNCTION_CALL",
    "reasoning": "Provide the user with actionable command-line steps to diagnose the Mattermost service issue.",
    "function_calls": [
        {
            "name": "respond_to_user",
            "parameters": {
                "response": "I'm sorry to hear that you're experiencing issues with Mattermost. Here are some command-line steps you can take to diagnose the problem:
                
                1. **Check Mattermost Service Status**
                   ```bash
                   sudo systemctl status mattermost
                   ```
                   Ensure that the Mattermost service is active and running.
                
                2. **Verify Listening Ports**
                   ```bash
                   sudo netstat -tulnp | grep :8065
                   ```
                   Replace `8065` with the port Mattermost is configured to use. This checks if Mattermost is listening on the expected port.
                
                3. **Examine Mattermost Logs**
                   ```bash
                   sudo journalctl -u mattermost -f
                   ```
                   Look for any error messages or warnings that could indicate the root cause.
                
                4. **Check Firewall Settings**
                   ```bash
                   sudo ufw status
                   ```
                   Ensure that the firewall isn't blocking the Mattermost port.
                
                5. **Test Database Connection**
                   ```bash
                   sudo -u mattermost psql -h <db_host> -U <db_user> -d <db_name> -c '\l'
                   ```
                   Replace `<db_host>`, `<db_user>`, and `<db_name>` with your database details to verify connectivity.
                
                6. **Inspect Network Configuration**
                   ```bash
                   ifconfig
                   ```
                   Ensure that the server's network interfaces are configured correctly and there are no IP conflicts.
                
                7. **Restart Mattermost Service**
                   ```bash
                   sudo systemctl restart mattermost
                   ```
                   Sometimes, simply restarting the service can resolve connectivity issues.
                
                If after performing these steps the issue persists, please provide any error logs or messages you encounter, and I'll be happy to assist further."
            }
        }
    ]
}
```"""
    ]
    for response in test_cases[-1:]:
        print(LLMCompletion.extract_json(response))