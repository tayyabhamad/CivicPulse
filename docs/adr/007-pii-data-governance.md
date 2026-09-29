# ADR 007: PII and data governance

Complaint text and optional contact details are treated as personal data.
The backend accepts only information required for operational follow-up, does
not log API keys, and keeps hosted-model credentials in environment variables
or deployment secrets. The OpenRouter adapter receives only complaint text and
location necessary for triage; it never receives repository credentials or
unrelated user data.

For demonstrations and tests, use seed fixtures rather than real citizen
contact details. Retention, deletion, and access policy must be defined by the
actual municipal deployment owner before production use; this coursework project
does not claim a production data-retention policy.
