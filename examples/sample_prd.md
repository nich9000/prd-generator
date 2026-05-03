# Saved Cart Recovery

> Customers who abandon a cart should get a one-tap recovery flow next time they open the app.

## Problem

Mobile shoppers regularly start a cart on one device, get distracted, and lose the items when they return. Today they have to re-find every product, costing 12-18% of returning sessions and biasing analytics toward "abandonment" when the real failure is *re-discovery*.

## Target user

Returning mobile shoppers who added 2+ items in their previous session within the last 14 days.

## Success metrics

- Reduce 14-day cart-abandonment rate from 71% to 60% (-11 pts) within 90 days of GA.
- Increase 14-day repeat-visit conversion by 8% relative.
- Recovery banner CTR ≥ 22% across iOS + Android.
- 95p time-to-recovered-cart < 800ms after app open.
- Less than 1% of restored carts contain stale (out-of-stock or repriced) items without a flag.

## User stories

**US-01 (P0).** As a **returning shopper**, I want to see a one-tap "Restore your cart" banner when I reopen the app so that I don't have to re-find products I already chose.

**US-02 (P0).** As a **returning shopper**, I want stale or repriced items to be clearly flagged before I check out so that I'm not surprised at payment.

**US-03 (P1).** As a **returning shopper**, I want to dismiss the recovery banner so that I'm not nagged when I came back for something else.

**US-04 (P1).** As a **shopper on a flaky connection**, I want the banner to load even if cart-sync is slow so that I'm not blocked by a spinner.

**US-05 (P2).** As a **returning shopper**, I want a small reminder on the home tab if I dismissed the banner so I can still recover later.

## Acceptance criteria

**AC-01**

- **Given** a user has an abandoned cart from the past 14 days
- **When** they open the app
- **Then** a recovery banner appears within 800ms of the home screen rendering

**AC-02**

- **Given** the abandoned cart contains an item that is out of stock or has changed price by ≥10%
- **When** the user taps "Restore"
- **Then** the cart loads with each affected item visibly flagged before they reach checkout

**AC-03**

- **Given** the user dismisses the recovery banner
- **When** they reopen the app within the same 14-day window
- **Then** the banner does not appear, but a smaller home-tab reminder is shown once

**AC-04**

- **Given** cart-sync fails or times out
- **When** the user opens the app
- **Then** no spinner blocks the home screen and the banner appears within 1500ms or is suppressed

## Requirements (EARS)

- **R-01** When the user opens the app and an abandoned cart exists from the last 14 days, the cart-recovery service shall render the recovery banner within 800 ms of home-screen first paint.
- **R-02** If a cart item is out of stock or has changed price by 10 percent or more, then the recovery flow shall display a stale-item flag adjacent to the item before checkout begins.
- **R-03** While the user is on the home tab and a banner has been dismissed in the current 14-day window, the recovery service shall surface a single home-tab reminder once per session.
- **R-04** If the cart-sync request fails or exceeds 1500 ms, then the recovery banner shall be suppressed without blocking other home-screen rendering.
- **R-05** The recovery service shall log a structured event for every banner shown, dismissed, or actioned, including item count, age in hours, and stale-item count.

## Risks

- **HIGH** — Stale-item flagging is wrong (price moves, partial OOS) and erodes trust faster than the recovery feature wins it back.
  *Mitigation:* Block GA on a 2-week beta where flagged-but-clean rate < 1% and unflagged-but-stale rate < 0.5%.
- **MEDIUM** — Banner cannibalizes the home-tab merchandising slot used for promotions.
  *Mitigation:* Run a 50/50 holdout for 30 days measuring incremental conversion *and* promo CTR; gate ramp on net positive both.
- **MEDIUM** — Cart-sync latency on cold app open already runs 1100ms p95; an 800ms target is aggressive.
  *Mitigation:* Pre-warm cart cache on push receipt; relax target to 1200ms if pre-warm not feasible in v1.
- **LOW** — Users find the home-tab reminder spammy.
  *Mitigation:* Cap to one reminder per 14-day window; instrument NPS on cohort.

## Out of scope

- Cross-device cart sync from web to mobile.
- Email or push notifications about abandoned carts (separate workstream).
- Recovery for guest checkouts.

## Open questions

- Do we suppress the banner during active promotional events that need the home slot?
- What's the right TTL for "stale" — 14 days for everything, or category-specific?
- Should the price-change threshold be percent, absolute, or whichever is greater?
