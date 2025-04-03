# Vertical Slice Architecture

This project follows a vertical slice architecture pattern, which organizes code by business feature rather than by technical layer.

## Structure

- `features/`: Contains business features as vertical slices
  - Each feature has its own API endpoints, services, and models
  - Features are independent and contain all necessary code
- `shared/`: Contains shared utilities used across features
- `config/`: Application configuration
- `tests/`: Integration and system-level tests

## Benefits

- Better organization - related code is kept together
- Easier to understand - each feature is self-contained
- Simplified maintenance - changes to one feature don't affect others
- Improved testability - features can be tested independently

## How to Add a New Feature

1. Create a new directory in `features/`
2. Create `__init__.py`, `api.py`, and `service.py` files
3. Register routes in the main `app.py`
