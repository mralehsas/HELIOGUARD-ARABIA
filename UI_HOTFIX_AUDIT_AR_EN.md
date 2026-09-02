# UI Hotfix Audit — v1.0.1

## Verified controls
- Language button: Arabic → English → Arabic.
- Root document language and direction: `ar/rtl` and `en/ltr`.
- About button: opens modal.
- Close button: closes modal.
- Arabic About section is visible in Arabic mode.
- English About section is visible in English mode.
- Connection Center button handler registers without a fatal JavaScript exception.

## Root cause
A selector was written as `$$('connectionCenterBtn')` although no `$$` helper existed. The resulting `ReferenceError` terminated execution before the language and About button listeners were registered.

## Browser harness result
`BROWSER_HARNESS_OK` — AR/EN switch, About open/close, language-specific About content, and label restoration passed.
