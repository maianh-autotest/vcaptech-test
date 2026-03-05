import { Page } from "@playwright/test";
import { resolvePopupOrCurrentPage } from "./page-utils";

const ROCSCIENCE_URL = "https://rocscience.com";

export class RocscienceHomePage {
  constructor(private readonly page: Page) {}

  async open(): Promise<void> {
    await this.page.goto(ROCSCIENCE_URL, { waitUntil: "domcontentloaded" });
  }

  async openRocportalLoginPage() {
    const profileTrigger = this.page.locator(
      `//a[@aria-label="Toggle Account Menu"]`,
    );
    await profileTrigger.click();

    const loginLink = this.page.locator(
      `//a[normalize-space()="Log in to RocPortal"]`,
    );

    return resolvePopupOrCurrentPage(this.page, async () => {
      await loginLink.click();
    });
  }
}
