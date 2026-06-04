---
name: feedback-jira-field-quirks
description: AC patterns, RN visibility trends, and low-trust field observations for Item Management Jira tickets
metadata:
  type: feedback
---

## AC patterns in Item Management

- Many foundational Item Management stories (especially in NXT-30027 overhaul epic) have very brief AC — often 2-4 bullet points that confirm sections load and save, without field-level detail. The Description field carries the bulk of field specifications in these older stories.
- Stories in NXT-45562 (Units Card Overhaul) and NXT-36067 (Item Units & Sub-types) have more substantive AC — these are the most reliable for feature behavior.
- When AC is empty or extremely brief, say so explicitly in metadata. Do not silently use Description as a substitute.

## RN Visibility patterns

- Most IM stories are RN: Not Required or blank — they are infrastructure/UX work not customer-announced.
- Stories with External/Internal RN text (highest content value): NXT-41273 (Images & Docs), NXT-43239 (Nutrient Details), NXT-47249 (Yield Factor).
- Stories with External Only: NXT-26906 (Menu Items History) — less relevant to create-item training.
- Use RN text as the customer-facing voice for content generation when available.

## Low-trust patterns

- Contribution Info stories (NXT-30102, NXT-37216) have no RN text and minimal AC. All meal-pattern field names should be marked [TO VERIFY] in drafts.
- Custom Allergen Configuration (NXT-24128) has detailed AC but no RN — the AC is the best source.
- Three-tier maximum pack size limit: not in any story AC. Referenced only in description language. Treat as presenter-stated fact, flag for editor verification.

## Match query efficiency notes

- 5+ word queries to `match` return nothing — keep to 2-4 words.
- "Contribution" queries consistently return no matches when combined with meal pattern terms. Use "contribution info card" or pull from epic context instead.
- "Custom allergen" returns the right ticket (NXT-24128) via "allergen custom configuration create".
- HACCP queries work best with "recipe steps directions HACCP" or "HACCP steps control points".

**Why:** Avoids wasted match queries and incorrect AC trust on Item Management tickets.
**How to apply:** On any new IM transcript, default to direct ticket lookups for the confirmed IDs in [[project-item-management-patterns]] rather than re-running match for known features.
