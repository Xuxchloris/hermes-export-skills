---
name: email-crafting
description: Use when a trade agent needs cold email, follow-up email, outreach copy, subject lines, reply drafts, personalization, multilingual trade email, or buyer-facing message drafts
---

# Email Crafting

## Overview

Write concise B2B trade emails grounded in prospect evidence and product facts. The core rule is that personalization must be earned by research, not invented.

## When to Use

Use this skill when the user asks for a first-touch email, follow-up sequence, reply to inquiry, catalog offer, sample discussion, or buyer-facing message.

Do not use it to send email automatically.

## Inputs

- Company research output
- Prospect score and priority
- Product context
- Tone rules from `TONE.yaml`
- Sender signature

## Outputs

```json
{
  "subject": "",
  "body": "",
  "cta": "",
  "personalization_evidence": [],
  "review_notes": []
}
```

## Procedure

1. Confirm the prospect priority is A or B. For C prospects, write only if the user explicitly asks. For D prospects, recommend no outreach.
2. Select one concrete personalization point from company research.
3. Select one matching product value point from product context.
4. Write a short subject line without spammy wording.
5. Write 120-160 words unless the user requests a different length.
6. Structure the body:
   - opening line based on prospect evidence
   - product relevance
   - one proof point such as certification, specification, or manufacturing capability
   - light CTA
   - signature
7. Add an opt-out line for regions where cold outreach compliance requires it.
8. Return review notes for any uncertain claims.

## Verification

- The email includes at least one evidence-backed personalization point.
- The email does not claim the prospect buys the product unless evidence says so.
- The email does not include unapproved prices.
- The CTA is light and specific.
- The output is a draft requiring human review.

## Common Mistakes

| Mistake | Fix |
| --- | --- |
| Writing "I saw you are looking for..." without proof | Say "I noticed you carry..." only when visible |
| Overloading first email with specifications | Mention one relevant proof point |
| Using aggressive sales language | Keep it professional and low-friction |
| Sending to D-level prospects | Recommend not contacting them |
