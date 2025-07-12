"""
Core Agent Manager - Handles AI agent interactions and code generation
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)


class AgentManager:
    """Manages AI agents for code generation and assistance"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.provider = config.get("provider", "ollama")
        self.model = config.get("model", "qwen2:7b")
        self.max_tokens = config.get("max_tokens", 4096)
        self.temperature = config.get("temperature", 0.1)

        # Service endpoints
        self.ollama_url = "http://localhost:11434"
        self.openwebui_url = "http://localhost:3000"

        # Client sessions
        self.http_client = None

        # Agent state
        self.conversation_history = []
        self.active_tasks = {}
        self.is_initialized = False

    async def initialize(self):
        """Initialize the agent manager"""
        try:
            logger.info(f"Initializing AgentManager with provider: {self.provider}")

            # Create HTTP client
            self.http_client = httpx.AsyncClient(timeout=30.0)

            # Check if required services are running
            await self._check_services()

            # Warm up the model
            await self._warmup_model()

            self.is_initialized = True
            logger.info("AgentManager initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing AgentManager: {e}")
            raise

    async def start(self):
        """Start the agent manager"""
        if not self.is_initialized:
            await self.initialize()
        logger.info("AgentManager started")

    async def stop(self):
        """Stop the agent manager"""
        if self.http_client:
            await self.http_client.aclose()
        logger.info("AgentManager stopped")

    async def health_check(self) -> bool:
        """Check if agent manager is healthy"""
        try:
            if not self.http_client:
                return False

            # Check Ollama health
            response = await self.http_client.get(f"{self.ollama_url}/api/tags")
            return response.status_code == 200

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    async def _check_services(self):
        """Check if required services are available"""
        try:
            # Check Ollama
            response = await self.http_client.get(f"{self.ollama_url}/api/tags")
            if response.status_code != 200:
                raise Exception("Ollama service not available")

            logger.info("Ollama service is available")

        except Exception as e:
            logger.error(f"Service check failed: {e}")
            raise

    async def _warmup_model(self):
        """Warm up the AI model"""
        try:
            logger.info(f"Warming up model: {self.model}")

            warmup_prompt = "Hello! Are you ready to help with coding tasks?"
            response = await self._generate_response(warmup_prompt)

            if response:
                logger.info("Model warmed up successfully")
            else:
                logger.warning("Model warmup failed")

        except Exception as e:
            logger.error(f"Model warmup error: {e}")

    async def generate_code(
        self,
        prompt: str,
        language: str = "python",
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate code based on prompt"""
        try:
            # Prepare the enhanced prompt
            enhanced_prompt = self._prepare_code_prompt(prompt, language, context)

            # Generate response
            response = await self._generate_response(enhanced_prompt)

            # Parse and validate the code
            result = self._parse_code_response(response, language)

            # Add to conversation history
            self.conversation_history.append(
                {
                    "type": "code_generation",
                    "prompt": prompt,
                    "language": language,
                    "response": result,
                    "timestamp": asyncio.get_event_loop().time(),
                }
            )

            return result

        except Exception as e:
            logger.error(f"Code generation error: {e}")
            return {"success": False, "error": str(e), "code": "", "explanation": ""}

    async def review_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Review and suggest improvements for code"""
        try:
            prompt = f"""Please review the following {language} code and provide:
1. Code quality assessment
2. Potential issues or bugs
3. Performance optimization suggestions
4. Best practices recommendations
5. Security considerations

Code to review:
```{language}
{code}
```

Please provide a structured response with specific suggestions."""

            response = await self._generate_response(prompt)

            result = {
                "success": True,
                "review": response,
                "language": language,
                "original_code": code,
            }

            return result

        except Exception as e:
            logger.error(f"Code review error: {e}")
            return {"success": False, "error": str(e)}

    async def fix_code(
        self, code: str, error_message: str, language: str = "python"
    ) -> Dict[str, Any]:
        """Fix code based on error message"""
        try:
            prompt = f"""The following {language} code has an error. Please fix it:

Error message:
{error_message}

Code with error:
```{language}
{code}
```

Please provide:
1. The corrected code
2. Explanation of what was wrong
3. Explanation of the fix

Format your response with the corrected code in a code block."""

            response = await self._generate_response(prompt)

            # Extract fixed code from response
            fixed_code = self._extract_code_from_response(response, language)

            result = {
                "success": True,
                "fixed_code": fixed_code,
                "explanation": response,
                "original_code": code,
                "error_message": error_message,
            }

            return result

        except Exception as e:
            logger.error(f"Code fix error: {e}")
            return {"success": False, "error": str(e)}

    async def generate_documentation(
        self, code: str, language: str = "python"
    ) -> Dict[str, Any]:
        """Generate documentation for code"""
        try:
            prompt = f"""Generate comprehensive documentation for the following {language} code:

```{language}
{code}
```

Please provide:
1. A clear description of what the code does
2. Parameter descriptions (if applicable)
3. Return value description (if applicable)
4. Usage examples
5. Any important notes or considerations

Format the documentation appropriately for {language}."""

            response = await self._generate_response(prompt)

            result = {
                "success": True,
                "documentation": response,
                "language": language,
                "original_code": code,
            }

            return result

        except Exception as e:
            logger.error(f"Documentation generation error: {e}")
            return {"success": False, "error": str(e)}

    def _prepare_code_prompt(
        self, prompt: str, language: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Prepare an enhanced prompt for code generation"""
        enhanced_prompt = f"""You are an expert {language} programmer.

Task: {prompt}

Please provide:
1. Clean, well-commented {language} code
2. Brief explanation of the approach
3. Any important considerations or assumptions

"""

        if context:
            enhanced_prompt += f"Additional context: {json.dumps(context, indent=2)}\n"

        enhanced_prompt += f"""
Please format your response with the code in a ```{language} code block.
Make sure the code follows best practices and is production-ready.
"""

        return enhanced_prompt

    async def _generate_response(self, prompt: str) -> str:
        """Generate response using the configured AI provider"""
        try:
            if self.provider == "ollama":
                return await self._generate_ollama_response(prompt)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")

        except Exception as e:
            logger.error(f"Response generation error: {e}")
            raise

    async def _generate_ollama_response(self, prompt: str) -> str:
        """Generate response using Ollama"""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.temperature,
                    "num_ctx": self.max_tokens,
                },
            }

            response = await self.http_client.post(
                f"{self.ollama_url}/api/generate", json=payload
            )

            response.raise_for_status()
            result = response.json()

            return result.get("response", "")

        except Exception as e:
            logger.error(f"Ollama response error: {e}")
            raise

    def _parse_code_response(self, response: str, language: str) -> Dict[str, Any]:
        """Parse code generation response"""
        try:
            # Extract code from response
            code = self._extract_code_from_response(response, language)

            # Extract explanation (text outside code blocks)
            explanation = self._extract_explanation_from_response(response)

            return {
                "success": True,
                "code": code,
                "explanation": explanation,
                "language": language,
                "full_response": response,
            }

        except Exception as e:
            logger.error(f"Response parsing error: {e}")
            return {
                "success": False,
                "error": str(e),
                "code": "",
                "explanation": "",
                "full_response": response,
            }

    def _extract_code_from_response(self, response: str, language: str) -> str:
        """Extract code from markdown code blocks"""
        import re

        # Look for code blocks with the specified language
        pattern = f"```{language}\\n(.*?)```"
        matches = re.findall(pattern, response, re.DOTALL)

        if matches:
            return matches[0].strip()

        # Fallback: look for any code blocks
        pattern = "```.*?\\n(.*?)```"
        matches = re.findall(pattern, response, re.DOTALL)

        if matches:
            return matches[0].strip()

        # If no code blocks found, return the response as-is
        return response.strip()

    def _extract_explanation_from_response(self, response: str) -> str:
        """Extract explanation text from response"""
        import re

        # Remove code blocks
        explanation = re.sub(r"```.*?```", "", response, flags=re.DOTALL)

        return explanation.strip()

    async def chat(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """General chat with the AI agent"""
        try:
            if context:
                enhanced_message = (
                    f"Context: {json.dumps(context)}\n\nMessage: {message}"
                )
            else:
                enhanced_message = message

            response = await self._generate_response(enhanced_message)

            # Add to conversation history
            self.conversation_history.append(
                {
                    "type": "chat",
                    "message": message,
                    "response": response,
                    "timestamp": asyncio.get_event_loop().time(),
                }
            )

            return response

        except Exception as e:
            logger.error(f"Chat error: {e}")
            return f"Sorry, I encountered an error: {e}"

    def get_conversation_history(
        self, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get conversation history"""
        if limit:
            return self.conversation_history[-limit:]
        return self.conversation_history

    def clear_conversation_history(self):
        """Clear conversation history"""
        self.conversation_history.clear()
        logger.info("Conversation history cleared")
