---
name: follow-up-planner
description: Use when a trade agent needs outreach follow-up timing, next-touch planning, reminder schedules, buyer reply follow-up, quotation follow-up, sample follow-up, or prospect status updates
---

# Follow-Up Planner

## Overview

Create a practical follow-up schedule from prospect priority and reply status. The core rule is to generate reviewable tasks, not automatic sends.

## When to Use

Use this skill after an outreach draft, buyer reply classification, quotation draft, sample discussion, or meeting request when the user needs the next-touch plan.

Use `reply-classification` first when an inbound reply has not been classified.

## Inputs

- Prospect priority from `prospect-scoring`
- Last contact date and channel
- Reply classification, if available
- Quotation, catalog, sample, or meeting status
- Tone rules from `TONE.yaml`

## Outputs

```json
{
  "prospect_status": "",
  "last_contact_date": "",
  "tasks": [
    {
      "due_date": "",
      "task_type": "",
      "reason": "",
      "draft_requested": false,
      "human_review_required": true
    }
  ],
  "pause_reason": "",
  "review_notes": []
}
```

## Procedure

1. Read the prospect priority, last contact date, and latest reply classification.
2. Pause planning when the prospect status does not call for another touch.
3. For an unanswered A or B prospect, suggest a light sequence such as D+3, D+7, and D+14 from the first outreach date.
4. For a quotation, catalog, sample, or meeting discussion, plan the next touch from the latest buyer-facing action.
5. Keep each task specific: due date, task type, reason, and whether an email draft is needed.
6. Send email draft requests to `email-crafting`.
7. Keep every task as a human-reviewed reminder.

## Verification

- Due dates are derived from the latest relevant contact.
- Task reasons match prospect status and buyer signals.
- Paused prospects receive no new follow-up task.
- The plan does not send messages automatically.
- Every generated task requires human review.

## Common Mistakes

| Mistake | Fix |
| --- | --- |
| Scheduling from an old contact date | Use the latest relevant action |
| Giving every prospect the same cadence | Consider priority and reply type |
| Creating vague reminders | Include due date, reason, and task type |
| Treating a task as an automatic send | Keep it as a human-reviewed reminder |
