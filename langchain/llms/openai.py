"""Wrapper around OpenAI APIs."""
import os
from typing import Any, Dict, List, Mapping, Optional

from pydantic import BaseModel, Extra, root_validator

from langchain.llms.base import LLM


class OpenAI(BaseModel, LLM):
    """Wrapper around OpenAI large language models.

    To use, you should have the ``openai`` python package installed, and the
    environment variable ``OPENAI_API_KEY`` set with your API key.

    Example:
        .. code-block:: python

            from langchain import OpenAI
            openai = OpenAI(model="text-davinci-002")
    """

    client: Any  #: :meta private:
    model_name: str = "text-davinci-002"
    """Model name to use."""
    temperature: float = 0.7
    """What sampling temperature to use."""
    max_tokens: int = 256
    """The maximum number of tokens to generate in the completion."""
    top_p: int = 1
    """Total probability mass of tokens to consider at each step."""
    frequency_penalty: int = 0
    """Penalizes repeated tokens according to frequency."""
    presence_penalty: int = 0
    """Penalizes repeated tokens."""
    n: int = 1
    """How many completions to generate for each prompt."""
    best_of: int = 1
    """Generates best_of completions server-side and returns the "best"."""

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that api key and python package exists in environment."""
        if "OPENAI_API_KEY" not in os.environ:
            raise ValueError(
                "Did not find OpenAI API key, please add an environment variable"
                " `OPENAI_API_KEY` which contains it."
            )
        try:
            import openai

            values["client"] = openai.Completion
        except ImportError:
            raise ValueError(
                "Could not import openai python package. "
                "Please it install it with `pip install openai`."
            )
        return values

    @property
    def _default_params(self) -> Mapping[str, Any]:
        """Get the default parameters for calling OpenAI API."""
        return {
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "n": self.n,
            "best_of": self.best_of,
        }

    def __call__(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """Call out to OpenAI's create endpoint.

        Args:
            prompt: The prompt to pass into the model.
            stop: Optional list of stop words to use when generating.

        Returns:
            The string generated by the model.

        Example:
            .. code-block:: python

                response = openai("Tell me a joke.")
        """
        response = self.client.create(
            model=self.model_name, prompt=prompt, stop=stop, **self._default_params
        )
        return response["choices"][0]["text"]
