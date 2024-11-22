### Message to client standard

```json
{
    "messages": [
        "this is a message",
        "this is another"
    ],
    "prompts": [
        {
            "text": ["this is a question?"],
            "input": "choice",
            "choices": [
                "choice",
                "other-choice"
            ],
            "options": {
                "handle": ["response", "second response"]
            }
        },
        {
            "text": ["info", "other question?"],
            "input": "string"
        }
    ]
}
```