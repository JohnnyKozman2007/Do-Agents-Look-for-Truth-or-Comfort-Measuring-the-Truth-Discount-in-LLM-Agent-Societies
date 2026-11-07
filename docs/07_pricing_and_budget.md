# Published API prices and pilot budget

Checked 6 November 2026. These are direct-provider standard synchronous prices in USD per million text tokens. Public catalog/model pages verify the configured IDs. Account access, settings compliance and actual billed spend remain untested.

| Configured model | Input | Output | Cached input |
| --- | ---: | ---: | ---: |
| [DeepSeek-V4-Flash / DeepInfra](https://deepinfra.com/deepseek-ai/DeepSeek-V4-Flash) | $0.09 | $0.18 | $0.018 |
| [Qwen3.8-Flash / DeepInfra](https://deepinfra.com/Qwen/Qwen3.8-Flash) | $0.113 | $0.382 | $0.0141 |
| [Claude Haiku 5.5 / Anthropic](https://platform.claude.com/docs/en/models/haiku-5-5/overview), prompt at most 100,000 tokens | $0.10 | $0.50 | $0.01 |
| [GPT-4o / OpenAI](https://developers.openai.com/api/docs/models/gpt-4o), secondary audit only | $2.50 | $10.00 | $1.25 |

Qwen cached input uses the public catalog's precision: input price multiplied by the cached-price ratio gives $0.01409999988, rounded to $0.0141. The model page displays $0.014. The proposed runtime manifest pins the more precise catalog rate.

Haiku's higher tier above 100,000 prompt tokens is $0.50 input, $2.50 output and $0.05 cached input for the whole request. The example manifest's 32,768-token input cap keeps requests within the short tier. Other routing tiers, cache writes and actual batch jobs have different prices.

## Explicit 624-town scenarios

Each scenario includes 312 towns per agent model, primary Haiku judging and a conditional future sample of 100 GPT-4o audit judgments. The current pilot collector does not automatically select or run the audit sample.

| Scenario | DeepSeek agents | Qwen agents | Haiku judge | 100 GPT-4o audit items | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| 700 input tokens/call, 50 chat calls and 8 primary judgments/town, 60 chat output and 100 judge output tokens | $1.3905 | $1.8948 | $0.5990 | $0.2750 | **$4.16** |
| 1,000 input tokens/call, maximum call path, configured output caps | $3.0562 | $4.2958 | $1.6848 | $0.5000 | **$9.54** |
| 1,500 input tokens/call, maximum call path, configured output caps | $4.3198 | $5.8823 | $2.0592 | $0.6250 | **$12.89** |

All rows include 12 decision calls per town at up to 5 output tokens. Maximum-path rows have 78 chat calls per town at up to 120 output tokens and 12 primary judgments at up to 250 output tokens. The 700-token working row uses 50 chat calls and 8 primary judgments. No row assumes cache hits, retries, taxes or payment fees. Fail-fast rejections that are retried cost nothing. A response without a cache count is recorded at the full input rate, so recorded spend can only overstate the bill. These are explicit planning assumptions, not measured tokens, confidence intervals or guaranteed upper bounds.

The old synthetic traces contain roughly 1,882 average input characters for judge calls, 2,376 for decisions and 2,792 for chat. Those character counts only motivate a starting token assumption. They are not model tokenizer measurements. A small authorized batch must supply actual usage before scaling the run.

The current scripted source makes no model call. Completed towns require 66–102 combined agent/primary-judge requests depending on mention paths. Across 624 towns this is 41,184–63,648 requests, before the separate audit and retries. Token prices alone do not establish runtime or account throughput.

## Settings and funding decisions

- DeepSeek reasoning must be explicitly disabled, for example with the documented `reasoning_effort: none`. Qwen's exact catalog entry is non-reasoning. A five-token cap and temperature zero do not prove valid or repeatable GO/SKIP behavior. [DeepInfra reasoning](https://docs.deepinfra.com/chat/reasoning)
- Haiku uses native disabled thinking. Its current API rejects temperature/top-p/top-k overrides. Hidden thinking still bills as output unless thinking is actually disabled. [Haiku migration](https://platform.claude.com/docs/en/models/haiku-5-5/migration-guide)
- Actual DeepInfra batch jobs receive a published 20% discount, and actual Anthropic/OpenAI batches receive 50%. This collector is synchronous, so its costs use the standard rates above. [DeepInfra Batch](https://docs.deepinfra.com/batch/introduction), [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing), [OpenAI Batch](https://developers.openai.com/api/docs/guides/batch)
- GPT-4o remains the configured secondary audit model. The current deprecation page lists a 14 January 2027 shutdown for the August/November snapshots. No replacement or snapshot change is automatic. [OpenAI deprecations](https://developers.openai.com/api/docs/deprecations)

The proposed $20 pilot ceiling is still a team funding decision. No payer, grant award, reimbursement or individual share is established by these scenarios. The existing credit-use hold remains until Ahmed explicitly releases it. OpenAI subscription API credits apply to the linked OpenAI organization, not direct DeepInfra or Anthropic bills. [OpenAI credit terms](https://developers.openai.com/api/docs/guides/chatgpt-api-credits)
