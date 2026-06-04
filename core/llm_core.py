# core/llm_core.py

import json
import os
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List

from dotenv.main import load_dotenv

load_dotenv()


# =====================================================
# BASE PROVIDER
# =====================================================

class LLMProvider(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def ready(self) -> bool:
        pass

    @abstractmethod
    def chat(
        self,
        prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 200
    ) -> Optional[str]:
        pass


# =====================================================
# OLLAMA
# =====================================================

class OllamaProvider(LLMProvider):

    def __init__(self, model: str = "jinx:latest"):
        self.model = model
        self._base_url = os.getenv("OLLAMA_API_BASE", "http://127.0.0.1:11434").rstrip("/")
        self._ready = False
        self._fallback_model = None

        try:
            import urllib.request
            import json

            req = urllib.request.Request(f"{self._base_url}/api/tags")
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read())
                available = [m["name"] for m in data.get("models", [])]

                if model in available:
                    self._ready = True
                elif available:
                    self._fallback_model = available[0]
                    self._ready = True

        except Exception as e:
            print(f"[Ollama] {e}")

    @property
    def ready(self):
        return self._ready

    @property
    def name(self):
        return f"ollama:{self.model}"

    def chat(
        self,
        prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 200,
        system: Optional[str] = None,
        think: bool = False
    ):

        if not self._ready:
            return None

        import urllib.request
        import json

        model = self.model if self._fallback_model is None else self._fallback_model
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = json.dumps({
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }).encode("utf-8")

        try:
            req = urllib.request.Request(
                f"{self._base_url}/api/chat",
                data=payload,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
                return data.get("message", {}).get("content", "").strip()

        except Exception as e:
            print(f"[Ollama Error] {e}")
            return None


# =====================================================
# GROQ
# =====================================================

class GroqProvider(LLMProvider):

    def __init__(
        self,
        model: str = "llama-3.3-70b-versatile"
    ):
        self.model = model
        self._client = None
        self._ready = False

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            return

        try:
            from groq import Groq

            self._client = Groq(api_key=api_key)
            self._ready = True

        except Exception as e:
            print(f"[Groq] {e}")

    @property
    def ready(self):
        return self._ready

    @property
    def name(self):
        return f"groq:{self.model}"

    def chat(
        self,
        prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 200
    ):

        if not self._ready:
            return None

        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"[Groq Error] {e}")
            return None


# =====================================================
# CLAUDE
# =====================================================

class ClaudeProvider(LLMProvider):

    def __init__(
        self,
        model: str = "claude-haiku-4-5-20251001"
    ):
        self.model = model
        self._client = None
        self._ready = False

        api_key = os.getenv("ANTHROPIC_API_KEY")

        if not api_key:
            return

        try:
            import anthropic

            self._client = anthropic.Anthropic(
                api_key=api_key
            )

            self._ready = True

        except Exception as e:
            print(f"[Claude] {e}")

    @property
    def ready(self):
        return self._ready

    @property
    def name(self):
        return f"claude:{self.model}"

    def chat(
        self,
        prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 200
    ):

        if not self._ready:
            return None

        try:
            response = self._client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            return response.content[0].text.strip()

        except Exception as e:
            print(f"[Claude Error] {e}")
            return None


# =====================================================
# JINX CORE
# =====================================================

class JinxLLMCore:

    def __init__(self):

        self.providers: Dict[str, LLMProvider] = {}

        self._load_providers()

    def _load_providers(self):

        candidates = [

            OllamaProvider(),

            GroqProvider(),

            ClaudeProvider(),

        ]

        for provider in candidates:

            if provider.ready:

                self.providers[
                    provider.name
                ] = provider

                print(
                    f"[READY] {provider.name}"
                )

    @property
    def available(self):

        return len(self.providers) > 0

    @property
    def provider_names(self):

        return list(
            self.providers.keys()
        )

    # =================================================
    # ASK MULTI PROVIDER
    # =================================================

    def ask(
        self,
        list_question: List[str],
        providers: Optional[List[str]] = None,
        temperature: float = 0.3,
        max_tokens: int = 200
    ) -> Dict[str, Any]:

        if providers is None:
            providers = self.provider_names

        results = {}

        for provider_name in providers:

            provider = self.providers.get(
                provider_name
            )

            if not provider:
                continue

            answers = []

            for question in list_question:

                answer = provider.chat(
                    prompt=question,
                    temperature=temperature,
                    max_tokens=max_tokens
                )

                answers.append({
                    "question": question,
                    "answer": answer
                })

            results[
                provider_name
            ] = answers

        return results

    # =================================================
    # ASK ONE QUESTION TO MANY MODELS
    # =================================================

    def ask_one(
        self,
        question: str,
        providers: Optional[List[str]] = None
    ):

        return self.ask(
            list_question=[question],
            providers=providers
        )


# =====================================================
# TEST
# =====================================================

if __name__ == "__main__":

    core = JinxLLMCore()

    print()
    print("Providers:")
    print(json.dumps(
        core.provider_names,
        indent=2,
        ensure_ascii=False
    ))

    list_question = [

        "ประเทศไทยมีกี่จังหวัด",

        "9.8 - 9.11 เท่ากับอะไร",

        "เขียน Python Hello World",

        "อธิบาย Quantum Computing 1 ประโยค"

    ]

    result = core.ask(

        list_question=list_question,

        providers=[
            "groq:llama-3.3-70b-versatile",
            "claude:claude-haiku-4-5-20251001",
            "ollama:jinx:latest"
        ]

    )

    print()
    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False
        )
    )