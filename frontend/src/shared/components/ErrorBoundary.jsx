// This is a placeholder file for ErrorBoundary.jsx
// Please paste the complete code from below in this file

/*
ErrorBoundary Component Guide:

This component catches JavaScript errors anywhere in its child component tree
and displays a fallback UI instead of crashing the entire application.

Features:
1. Catches errors in components during rendering, lifecycle methods, and event handlers
2. Logs error information to the console (and potentially to a monitoring service)
3. Displays a user-friendly error message
4. Provides a way to recover (reset the error state and retry)

How to use:
- Wrap components that might throw errors with this ErrorBoundary
- Use multiple ErrorBoundary components to isolate errors to specific parts of the UI
- Consider wrapping route components to prevent entire app crashes
- Pass custom fallback UI via props if desired
*/
