import { expect, Locator, Page } from "@playwright/test";

const EXPECTED_LOGIN_PATH = "https://auth.rocscience.com/u/login";

export class RocportalLoginPage {
  constructor(private readonly page: Page) {}

  private emailInput(): Locator {
    return this.page.locator(`//input[@id="username"]`);
  }

  private passwordInput(): Locator {
    return this.page.locator(`//input[@id="password"]`);
  }

  private loginButton(): Locator {
    return this.page.locator(`//button[text()="Continue"]`);
  }

  async assertLoaded(): Promise<void> {
    await expect
      .poll(async () => this.page.url(), {
        message: "Expected login page URL to include /auth/login",
      })
      .toContain(EXPECTED_LOGIN_PATH);
  }

  async assertRequiredControlsVisible(): Promise<void> {
    const emailInput = this.emailInput();
    const passwordInput = this.passwordInput();
    const loginButton = this.loginButton();

    await expect(emailInput).toBeVisible();
    await expect(passwordInput).toBeVisible();
    await expect(loginButton).toBeVisible();
    await expect(loginButton).toBeEnabled();
  }
}
