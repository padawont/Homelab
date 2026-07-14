---
title: "SDK Structured Output"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - sdk
  - javascript
  - typescript
  - structured-output
sources:
  - url: "https://opencode.ai/docs/sdk"
    title: "OpenCode SDK Documentation"
  - url: "https://opencode.ai/docs/server"
    title: "OpenCode Server Documentation"
last_audit_date: 2026-06-07
---

# SDK Structured Output

The SDK supports requesting structured (typed) responses from the model via the `format` option. This enforces a JSON Schema on the model's reply.

```ts
const result = await client.session.prompt({
  path: { id: sessionId },
  body: {
    parts: [{ type: "text", text: "Research Anthropic" }],
    format: {
      type: "json_schema",
      schema: {
        type: "object",
        properties: {
          company: { type: "string", description: "Company name" },
          founded: { type: "number", description: "Year founded" },
          products: {
            type: "array",
            items: { type: "string" },
            description: "Main products",
          },
        },
        required: ["company", "founded"],
      },
    },
  },
});

// Access the structured output
console.log(result.data.info.structured_output);
// { company: "Anthropic", founded: 2021, products: ["Claude", "Claude API"] }
```

## Output Format Types

| Type | Description |
|---|---|
| `text` | Default. Standard text response (no structured output) |
| `json_schema` | Returns validated JSON matching the provided schema |

## JSON Schema Format Options

| Field | Type | Description |
|---|---|---|
| `type` | `"json_schema"` | Required. Specifies JSON schema mode |
| `schema` | `object` | Required. JSON Schema object defining the output structure |
| `retryCount` | `number` | Optional. Number of validation retries (default: 2) |

## Best Practices

1. **Provide clear descriptions** in your schema properties to help the model understand what data to extract.
2. **Use `required`** to specify which fields must be present.
3. **Keep schemas focused** — complex nested schemas may be harder for the model to fill correctly.
4. **Set appropriate `retryCount`** — increase for complex schemas, decrease for simple ones.

## Error Handling

Structured output validation failures are returned on the response data under `info.error`, not thrown. When the model fails to produce valid JSON after all retries, a `StructuredOutputError` is set. See [SDK Error Handling](./error-handling.md#structured-output-validation-failures) for the full error-handling pattern.
