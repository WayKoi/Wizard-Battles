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
            ]
        },
        {
            "text": ["info", "other question?"],
            "input": "string"
        }
    ]
}
```