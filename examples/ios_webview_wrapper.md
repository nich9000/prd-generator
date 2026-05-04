# iOS App via WebView Wrapper

> Ship our existing mobile-web shopping experience as a native iOS app using a WebView wrapper, so customers can install us from the App Store and we can use push notifications, biometric unlock, and Apple Pay without rebuilding the storefront.

## Problem

Customers cannot install our storefront from the App Store, leaving us without access to native iOS capabilities — push notifications, biometric authentication, and Apple Pay — that reduce friction and drive repeat purchases. Building a fully native app is prohibitively slow, so a WebView wrapper lets us ship these capabilities against our existing mobile-web codebase.

## Target user

Existing and prospective customers who shop on iOS and prefer or expect a native app experience, particularly repeat buyers who would benefit from saved credentials, payment shortcuts, and timely promotional alerts.

## Success metrics

- Achieve an App Store rating of 4.3 stars or higher within 90 days of launch, measured across a minimum of 500 ratings.
- Push notification opt-in rate of at least 45% among users who complete their first app session within the first 60 days.
- Apple Pay adoption on at least 30% of all iOS app transactions within 90 days, compared to 0% on mobile web today.
- 30-day retention rate for app users is at least 10 percentage points higher than the 30-day return rate for mobile-web users in the same cohort period.
- App store page load time (WebView fully interactive) remains under 3 seconds on an iPhone 12 or newer on a 4G connection for at least 95% of sessions.

## User stories

**US-01 (P0).** As a **iOS shopper**, I want to download and install the app from the App Store and have the storefront WebView become fully interactive within 3 seconds on a 4G connection so that I can start browsing without frustrating load delays that would cause me to abandon the app immediately.

**US-02 (P0).** As a **iOS shopper completing a purchase**, I want to pay using Apple Pay with a single Face ID or Touch ID confirmation inside the app so that I can check out faster without manually entering card details, reducing friction that would otherwise cause me to abandon my cart.

**US-03 (P0).** As a **first-time app user who has just completed my initial session**, I want to be prompted once to allow push notifications via a native iOS permission dialog, presented at a contextually appropriate moment after I have experienced app value so that I can receive timely promotional alerts and order updates that bring me back to the app and drive repeat purchases.

**US-04 (P1).** As a **returning iOS shopper**, I want to authenticate into my account using Face ID or Touch ID instead of typing my password so that I can access my saved addresses and order history quickly, making repeat purchases feel seamless and encouraging me to return.

**US-05 (P1).** As a **iOS shopper on a degraded or offline network**, I want to see a clear, branded error screen with a retry action when the WebView fails to load rather than a blank white page or a generic browser error so that I understand what went wrong and can recover without losing trust in the app, protecting our App Store rating.

**US-06 (P1).** As a **iOS shopper who taps a deep-link in a push notification**, I want to be taken directly to the promoted product or offer page inside the app rather than landing on the homepage so that the promotional message delivers on its promise and I can act on the offer without extra navigation steps that reduce conversion.

**US-07 (P1).** As a **iOS shopper whose device does not support Face ID or Touch ID**, I want to fall back gracefully to standard email-and-password login when biometric authentication is unavailable or disabled so that I am never locked out of my account due to a missing hardware capability, ensuring the app is usable across all supported devices.

**US-08 (P2).** As a **shopper who declines the push notification permission prompt**, I want to continue using the app without repeated re-prompting during the same session and without any degraded shopping functionality so that I do not feel harassed into granting permissions, which would otherwise lead to negative App Store reviews that drag our rating below 4.3 stars.

## Acceptance criteria

**AC-01**

- **Given** An iOS device connected to a 4G network (minimum 12 Mbps download) with the app freshly installed from the App Store
- **When** The user launches the app for the first time
- **Then** The storefront WebView must fire its 'page interactive' event (DOMContentLoaded + first meaningful paint) within 3 seconds of app launch, measurable via instrumented performance logging

**AC-02**

- **Given** An iOS device connected to a 4G network with the app installed
- **When** The user launches the app and the WebView begins loading
- **Then** A loading indicator is displayed immediately (within 100 ms of launch) and disappears once the WebView is interactive, ensuring no blank white screen is shown at any point during the load sequence

**AC-03**

- **Given** An iOS shopper with a valid Apple Pay payment method configured on their device and items in their cart
- **When** The shopper taps the Apple Pay button and confirms the payment sheet using Face ID or Touch ID
- **Then** The purchase is authorized and a confirmation screen is displayed within 5 seconds, with no manual card-detail entry required at any step

**AC-04**

- **Given** An iOS shopper attempts Apple Pay checkout but Face ID or Touch ID authentication fails three consecutive times
- **When** The biometric authentication is rejected
- **Then** The Apple Pay sheet is dismissed, no charge is applied, and the shopper is returned to the cart with an error message indicating the payment was not completed

**AC-05**

- **Given** A first-time user who has completed at least one meaningful in-app action (e.g., viewed a product detail page or added an item to the cart) during their initial session
- **When** The contextual trigger condition is met for the first time
- **Then** The native iOS push notification permission dialog is presented exactly once per app install, and no custom pre-prompt or repeated system prompt is shown within the same session

**AC-06**

- **Given** A first-time user who has not yet been shown the push notification permission dialog
- **When** The user completes their first session without triggering the contextual prompt condition
- **Then** The native iOS permission dialog is not shown until the qualifying contextual moment is reached, and it is never shown more than once regardless of subsequent sessions

**AC-07**

- **Given** A returning iOS shopper with biometric authentication enabled on their device and a valid stored session credential
- **When** The shopper opens the app and initiates login
- **Then** A Face ID or Touch ID prompt is presented, and upon successful biometric confirmation the shopper is logged in and lands on their account home screen within 2 seconds, with no password entry required

**AC-08**

- **Given** A returning iOS shopper attempts biometric login but provides an incorrect biometric three consecutive times
- **When** The system exhausts the biometric retry limit
- **Then** The biometric prompt is dismissed, the shopper is presented with the email-and-password login form, and no account lockout is triggered solely due to biometric failure

**AC-09**

- **Given** An iOS shopper whose device has no active network connection or is on a degraded connection that causes the WebView to time out after 10 seconds
- **When** The WebView fails to load
- **Then** A branded error screen containing the app logo, a human-readable error message, and a 'Retry' button is displayed in place of the WebView within 1 second of the failure event, with no blank white page or generic browser error shown at any point

**AC-10**

- **Given** An iOS shopper is viewing the branded offline error screen
- **When** The shopper taps the 'Retry' button and a network connection is available
- **Then** The WebView reload is initiated immediately and the storefront becomes interactive within 3 seconds on a 4G connection, returning the shopper to the same URL that originally failed

**AC-11**

- **Given** An iOS shopper has granted push notification permission and the app is in the background or closed
- **When** The shopper taps a push notification containing a valid deep-link URL to a specific product or offer page
- **Then** The app opens and the WebView navigates directly to the deep-linked product or offer page within 3 seconds, bypassing the homepage entirely

**AC-12**

- **Given** An iOS shopper taps a push notification containing a deep-link URL that references a product or offer that is no longer available
- **When** The WebView attempts to load the deep-linked page
- **Then** The app displays a relevant error or 'item unavailable' page rather than the homepage or a blank screen, and a navigation path back to the storefront homepage is accessible within one tap

**AC-13**

- **Given** An iOS shopper is using a device that does not have Face ID or Touch ID hardware, or has biometrics disabled in device settings
- **When** The shopper opens the app and initiates login
- **Then** The biometric prompt is never shown; instead, the email-and-password login form is presented immediately, and the shopper can successfully authenticate and access all account features

**AC-14**

- **Given** An iOS shopper has biometrics available on their device but declines to enroll or disables the feature within the app's settings
- **When** The shopper initiates login
- **Then** The app falls back to the email-and-password login form without displaying any error related to biometrics, and the shopper can complete login without being prompted to re-enable biometrics during that session

**AC-15**

- **Given** A shopper who has declined the native iOS push notification permission prompt
- **When** The shopper continues browsing, adds items to the cart, and completes a purchase within the same session
- **Then** No second push notification permission prompt (native or custom) is displayed during that session, and all shopping features — including cart, checkout, and order confirmation — function identically to the experience of a shopper who granted permission

**AC-16**

- **Given** A shopper who declined push notification permission in a previous session relaunches the app
- **When** The shopper uses the app across multiple subsequent sessions
- **Then** The native iOS push notification permission dialog is never re-triggered by the app (since iOS prevents re-prompting after denial), and no custom in-app modal requesting notification permission is displayed more than zero additional times after the initial decline

## Requirements (EARS)

- **R-01** When the user launches the app for the first time on an iOS device connected to a 4G network (minimum 12 Mbps download) with the app freshly installed, the storefront WebView shall fire its 'page interactive' event (DOMContentLoaded + first meaningful paint) within 3 seconds of app launch, as recorded by instrumented performance logging.
- **R-02** When the app is launched and the WebView begins loading, the app shall display a loading indicator within 100 milliseconds of launch and keep it visible until the WebView is interactive, ensuring no blank white screen is shown at any point during the load sequence.
- **R-03** When an iOS shopper with a valid Apple Pay payment method and items in their cart taps the Apple Pay button and confirms the payment sheet using Face ID or Touch ID, the app shall authorize the purchase and display a confirmation screen within 5 seconds, with no manual card-detail entry required at any step.
- **R-04** If Face ID or Touch ID authentication for Apple Pay fails three consecutive times, then the app shall dismiss the Apple Pay sheet, apply no charge, and return the shopper to the cart with an error message indicating the payment was not completed.
- **R-05** When a first-time user who has completed at least one meaningful in-app action (e.g., viewed a product detail page or added an item to the cart) meets the contextual trigger condition for the first time, the app shall present the native iOS push notification permission dialog exactly once per app install, without showing any custom pre-prompt or repeating the system prompt within the same session.
- **R-06** When a first-time user completes their first session without triggering the contextual push notification prompt condition, the app shall withhold the native iOS push notification permission dialog until the qualifying contextual moment is reached, and shall never display it more than once regardless of subsequent sessions.
- **R-07** When a returning iOS shopper with biometric authentication enabled and a valid stored session credential opens the app and initiates login, the app shall present a Face ID or Touch ID prompt and, upon successful biometric confirmation, log the shopper in and navigate to their account home screen within 2 seconds, with no password entry required.
- **R-08** If a returning iOS shopper provides an incorrect biometric three consecutive times and the system exhausts the biometric retry limit, then the app shall dismiss the biometric prompt, present the email-and-password login form, and trigger no account lockout solely due to biometric failure.
- **R-09** If the WebView fails to load because the device has no active network connection or a degraded connection causes a timeout after 10 seconds, then the app shall display a branded error screen containing the app logo, a human-readable error message, and a 'Retry' button in place of the WebView within 1 second of the failure event, with no blank white page or generic browser error shown at any point.
- **R-10** When an iOS shopper viewing the branded offline error screen taps the 'Retry' button and a network connection is available, the app shall initiate a WebView reload immediately, make the storefront interactive within 3 seconds on a 4G connection, and navigate to the same URL that originally failed.
- **R-11** When an iOS shopper who has granted push notification permission taps a push notification containing a valid deep-link URL to a specific product or offer page, the app shall open and navigate the WebView directly to the deep-linked product or offer page within 3 seconds, bypassing the homepage entirely.
- **R-12** If the WebView attempts to load a deep-linked page referencing a product or offer that is no longer available, then the app shall display a relevant error or 'item unavailable' page rather than the homepage or a blank screen, and provide a navigation path back to the storefront homepage that is accessible within one tap.
- **R-13** When an iOS shopper on a device that lacks Face ID or Touch ID hardware, or has biometrics disabled in device settings, opens the app and initiates login, the app shall never show the biometric prompt, present the email-and-password login form immediately, and allow the shopper to successfully authenticate and access all account features.
- **R-14** When an iOS shopper who has declined biometric enrollment or disabled the biometric feature in app settings initiates login, the app shall fall back to the email-and-password login form without displaying any biometric-related error, and complete login without prompting the shopper to re-enable biometrics during that session.
- **R-15** While a shopper has declined the native iOS push notification permission prompt and is continuing to browse, add items to the cart, or complete a purchase within the same session, the app shall display no second push notification permission prompt (native or custom) and provide cart, checkout, and order confirmation functionality identical to that of a shopper who granted permission.
- **R-16** While a shopper who declined push notification permission in a previous session is using the app across one or more subsequent sessions, the app shall never re-trigger the native iOS push notification permission dialog and display no custom in-app modal requesting notification permission on any occasion after the initial decline.

## Risks

- **HIGH** — Apple App Store rejection due to WebView-only content policy. Apple's guideline 4.2 ('Minimum Functionality') and 2.12 reject apps that are little more than a web browser. If reviewers classify the wrapper as providing insufficient native value beyond Safari, the app will be rejected or removed post-launch, blocking the entire initiative.  
  *Mitigation:* Ensure the app demonstrably uses native APIs (Apple Pay, biometrics, push notifications) that are impossible in Safari. Document these native integrations explicitly in the App Store review notes. Engage an App Store specialist to pre-review the submission and prepare a clear rejection appeal. Avoid generic UserAgent strings that signal pure WebView to reviewers.
- **HIGH** — Apple Pay JS/WebView bridge integration failure causing checkout breakage. The Apple Pay JS API must be invoked from a WKWebView with correctly configured merchant domain verification, entitlements, and a valid payment processing certificate. A misconfiguration in any layer—domain association file, entitlement, or the native-JS bridge—silently prevents the payment sheet from appearing, causing 100% checkout failure for Apple Pay and missing the 30% adoption metric.  
  *Mitigation:* Build and test the Apple Pay bridge end-to-end in a sandbox environment before any beta. Write automated integration tests that exercise the WKWebView-to-native delegate flow. Confirm merchant domain verification files are deployed and accessible before submission. Define a feature flag to disable Apple Pay at runtime if production errors spike, falling back to card entry.
- **HIGH** — WebView load-time SLA failure on real-world networks causing immediate user drop-off and poor ratings. The 3-second interactive threshold on iPhone 12 / 4G is tight given the existing mobile-web bundle size. Any regression in web asset size, CDN latency, or WKWebView cold-start overhead could push p95 load times above 3 seconds, directly triggering abandonment and 1–2 star reviews before a fix can be shipped.  
  *Mitigation:* Instrument real-user monitoring (RUM) with a WebView-to-native timing bridge reporting to an observability platform from day one. Pre-warm the WKWebView process pool and pre-cache critical assets via URLCache on app launch. Set a CI performance budget that fails the build if Lighthouse mobile score drops below a threshold. Establish an on-call alert if p95 load time exceeds 2.5 seconds in production.
- **MEDIUM** — Push notification opt-in rate falls below 45% because the prompt fires at the wrong moment, wasting the single iOS permission request. iOS only allows one native permission prompt; if it appears too early (e.g., on app open before any value is demonstrated) the majority of users will decline, with no programmatic recovery path short of guiding users to Settings manually.  
  *Mitigation:* Gate the native permission request behind an in-app soft prompt (custom UI) that explains value first, shown only after a user completes a meaningful action (e.g., first browse of a category or after order confirmation). A/B test the trigger moment in a limited rollout before broad launch. Instrument decline rates by trigger point and iterate on placement before the 60-day opt-in metric is evaluated.
- **MEDIUM** — Go-to-market risk: Low App Store discoverability and slow rating accumulation mean the 500-rating / 4.3-star threshold is not reached within 90 days. Without an existing iOS install base, organic ratings accrue slowly; a small number of negative reviews from performance or login issues in early weeks can anchor the average below 4.3 stars before positive volume catches up.  
  *Mitigation:* Launch a targeted email and push (web) campaign to the existing mobile-web customer base to drive early installs from engaged users most likely to leave positive reviews. Integrate an in-app review prompt (SKStoreReviewAPI) triggered after a confirmed successful purchase—the highest-satisfaction moment. Monitor ratings daily in the first 30 days; triage and hotfix any issue pattern appearing in 1–2 star reviews before it compounds.
- **MEDIUM** — Biometric credential storage misconfiguration exposing stored tokens or locking users out after OS upgrades. If the Keychain item accessibility attribute is set too permissively (e.g., kSecAttrAccessibleAlways) or the biometric policy binding is incorrect, stored auth tokens could be accessible without authentication or could be invalidated after an iOS update or biometric re-enrollment, silently logging all returning users out and generating negative reviews and support volume.  
  *Mitigation:* Use kSecAttrAccessibleWhenPasscodeSetThisDeviceOnly with LAContext biometric binding for all stored credentials. Write unit tests covering Keychain read/write under simulated biometric-invalidation conditions. Implement a graceful fallback (story already scoped for P1) that detects Keychain retrieval failure and routes to password login with a clear, non-alarming message. Conduct a security review of Keychain usage before submission.

## Out of scope

- Android app or Android WebView wrapper
- Full native iOS rewrite replacing the WebView approach
- In-app purchase or App Store subscription billing (IAP)
- Native iOS widgets or App Clips
- Web push notifications for the mobile-web channel (non-app)
- iPad-specific layout optimizations
- Accessibility / WCAG compliance remediation of the underlying mobile-web codebase
- Backend changes to the storefront API or checkout service

## Open questions

- Which merchant payment processor will handle Apple Pay, and has the merchant identifier and payment processing certificate already been provisioned? What is the lead time if not?
- What is the current mobile-web p95 Time-to-Interactive on 4G, and has a performance baseline been established to determine the gap to the 3-second SLA before development begins?
- How will authenticated sessions be shared or bridged between the existing mobile-web session (cookie/token) and the native Keychain-backed biometric credential to avoid forcing re-login on first app launch?
- What push notification platform will be used for APN delivery (e.g., Firebase, Braze, custom), and who owns the campaign tooling and segmentation for the promotional alerts?
- Does the existing mobile-web storefront require Content Security Policy changes to permit the WKWebView origin, and who owns that change in the web team?
- What is the minimum supported iOS version, and how does that affect WKWebView API availability and the biometric API surface (e.g., LAContext availability on older OS versions)?
