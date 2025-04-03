# SASS Architecture Guide

## Structure
```
styles/
├── base/          # Global base styles
│   ├── reset.scss
│   └── typography.scss
├── components/    # Component-specific styles
├── layout/        # Layout components (header, footer, etc.)
├── utilities/     # Helper classes and mixins
│   └── _variables.scss
└── main.scss      # Main entry point
```

## Usage

### Variables
Import variables in your components:
```scss
@use 'utilities/variables' as v;

.button {
  background-color: v.$primary-color;
  color: v.$text-light;
}
```

### With Tailwind
The `main.scss` already includes Tailwind directives. Any new styles should:
1. Use SASS variables where possible
2. Only override Tailwind when necessary
3. Follow the utility-first approach

## Migration Steps
1. Create new component styles in `components/`
2. Import them in `main.scss`
3. Reference variables from `_variables.scss`
4. Remove old CSS files after migration