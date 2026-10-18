from openai import APIConnectionError, APIStatusError, APITimeoutError

from parallax.config import get_settings
from parallax.llm.client import get_llm_client


def main() -> None:
    settings = get_settings()
    client = get_llm_client()

    print(f"Testing model: {settings.openrouter_model}")

    try:
        response = client.chat.completions.create(
            model=settings.openrouter_model,
            messages=[
                {
                    "role": "user",
                    "content": "Reply with exactly: Parallax connection successful.",
                }
            ],
            max_tokens=150,
        )

        choice = response.choices[0]
        message = choice.message

        print("Request successful.")
        print("Model returned:", response.model)
        print("Finish reason:", choice.finish_reason)
        print("Message content:", repr(message.content))
        print("Refusal:", message.refusal)
        print("Usage:", response.usage)

        if message.content is None:
            print("No text content returned; inspect the metadata above.")
        else:
            print("Text response:", message.content)

    except APIStatusError as exc:
        print(f"OpenRouter returned HTTP {exc.status_code}.")
        print("Check the error category and account access.")
        print("Do not increase the credit limit or add credits.")

    except (APIConnectionError, APITimeoutError):
        print("Could not connect to OpenRouter or the request timed out.")


if __name__ == "__main__":
    main()
