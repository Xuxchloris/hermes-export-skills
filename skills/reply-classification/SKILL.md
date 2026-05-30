---
name: reply-classification
description: Use when a trade agent needs to classify buyer replies, inquiry responses, catalog requests, sample requests, quotation requests, objections, unsubscribe messages, or unclear inbound email
---

# Reply Classification

## Overview

Classify buyer replies into a clear sales status and recommend the next human-reviewed action. The core rule is to preserve the buyer's intent without inventing commitment or urgency.

## When to Use

Use this skill after an inbound buyer email, message, or reply arrives and the user wants to know what it means or what to do next.

Use `email-crafting` after classification when a reply draft is needed.

## Inputs

- Buyer reply text
- Prospect score and company research output
- Previous outreach summary
- Product and pricing context, when relevant

## Outputs

```json
{
  "classification": "inquiry|quotation_request|catalog_request|sample_request|meeting_request|objection|not_interested|unsubscribe|out_of_office|unclear",
  "confidence": "low|medium|high",
  "buyer_signals": [],
  "requested_items": [],
  "missing_information": [],
  "recommended_action": "",
  "reply_draft_needed": false,
  "human_review_required": true
}
```

## Procedure

1. Extract the buyer's explicit request, product references, quantities, destination, deadline, and questions.
2. Select one classification that best matches the reply. Use `unclear` when the message needs human judgment.
3. Record buyer signals as observed facts only.
4. List commercial details that still need confirmation.
5. Recommend one next action: reply, prepare quotation draft, send catalog draft, discuss sample, schedule meeting, pause follow-up, or request human review.
6. Send quotation requests to `quotation-generator`.
7. Send reply drafting requests to `email-crafting`.

## Verification

- Classification matches the buyer's explicit message.
- Buyer intent is not overstated.
- Missing quantity, SKU, destination, or commercial terms are listed when relevant.
- Recommended action is specific and human-reviewed.
- Unclear replies remain `unclear`.

## Common Mistakes

| Mistake | Fix |
| --- | --- |
| Treating a polite reply as buying intent | Record the exact buyer signal |
| Drafting a quote without required details | Pass missing fields to quotation workflow |
| Guessing the requested product | Ask for clarification |
| Continuing outreach after unsubscribe | Recommend pausing follow-up |
