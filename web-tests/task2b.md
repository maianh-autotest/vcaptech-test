# Task 2B — API Thinking for Invalid Login (Using Playwright)

## Overview

The goal of this task is to verify that the login process **fails correctly when invalid credentials are provided**, using **API-level validation** instead of UI automation.

Since real credentials are not required, this example assumes a reasonable backend login API endpoint and demonstrates how the validation would work.

---

# 1. Endpoint URL and HTTP Method

**Assumed API Endpoint**

- **Method:** `POST`
- **URL:**

```
https://example.com/api/v1/auth/login
```

**How to discover the real endpoint using DevTools**

1. Open the application's **login page**.
2. Press **F12** to open browser Developer Tools.
3. Navigate to the **Network** tab.
4. Filter requests by **Fetch/XHR**.
5. Attempt a login with any credentials.
6. Locate the request related to authentication (often named `login`, `auth`, `session`, or `token`).
7. Inspect the request to identify:
   - Request URL
   - HTTP Method
   - Request Payload
   - Response status and response body

---

# 2. Example Request Payload

Most authentication APIs use **JSON** request bodies.

Example request payload:

```json
{
  "email": "wrong@example.com",
  "password": "incorrect_password"
}
```

Example request headers:

```
Content-Type: application/json
```

---

# 3. Response Signals That Indicate Login Failure

Login failure can be verified using several signals from the API response.

### 1. HTTP Status Code

Typical failure codes include:

- `401 Unauthorized`
- `403 Forbidden`
- `400 Bad Request`

Example:

```
HTTP/1.1 401 Unauthorized
```

---

### 2. Error Message in Response Body

Example response body:

```json
{
  "error": "INVALID_CREDENTIALS",
  "message": "Email or password is incorrect"
}
```

---

### 3. Authentication Token is Missing

On successful login, APIs usually return a token such as:

- `access_token`
- `token`
- session cookie

For invalid credentials, the response **must not contain** any authentication token.

---

# 4. Playwright Code Snippet to Verify Login Failure

The following Playwright test sends an API request with invalid credentials and verifies that authentication fails.

```ts
import { test, expect } from "@playwright/test";

test("API login should fail for invalid credentials", async ({ request }) => {
  const endpoint = "https://example.com/api/v1/auth/login";

  const payload = {
    email: "wrong@example.com",
    password: "incorrect_password",
  };

  const response = await request.post(endpoint, {
    data: payload,
    headers: {
      "Content-Type": "application/json",
    },
  });

  // Verify status code indicates authentication failure
  expect([400, 401, 403]).toContain(response.status());

  // Parse response body
  const body = await response.json().catch(() => ({}));

  // Verify that no authentication token is returned
  expect(body.access_token ?? body.token ?? null).toBeNull();

  // Verify error message indicates invalid credentials
  const message = (body.error ?? body.message ?? "").toLowerCase();

  expect(
    message.includes("invalid") ||
      message.includes("incorrect") ||
      message.includes("unauthorized") ||
      message.includes("credentials"),
  ).toBeTruthy();
});
```

---

