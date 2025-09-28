from openai import OpenAI
import os
import sys

def main():
    key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("LLM_SWAP_MODEL", "gpt-4o-mini")
    print("OPENAI_API_KEY set:", bool(key))
    print("Model to test:", model)

    # Construct client; if key is not set this will use default config and likely fail
    client = OpenAI(api_key=key) if key else OpenAI()

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Hello"}],
            temperature=0,
        )
        print("OK - got response object of type:", type(resp))
        # print small summary without exposing secrets
        try:
            choices = getattr(resp, "choices", None)
            if choices:
                print("First choice content (truncated):", str(choices[0].message.content)[:200])
        except Exception:
            pass
    except Exception as e:
        print("ERROR connecting to OpenAI:", type(e).__name__, str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()
# test_model_access.py
from openai import OpenAI
import os
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = os.getenv("LLM_SWAP_MODEL", "gpt-4o-mini")
try:
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role":"user","content":"Say hi"}],
        temperature=0
    )
    print("OK - response type:", type(resp))
except Exception as e:
    print("ERROR:", e)