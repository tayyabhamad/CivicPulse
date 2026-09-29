# ADR 002: API contract

FastAPI response models produce the checked-in OpenAPI schema. Generated frontend types are checked against that schema, while browser calls stay relative to `/api`; nginx supplies environment-specific routing at runtime.
