import { Page } from "@playwright/test";

export async function resolvePopupOrCurrentPage(page: Page, action: () => Promise<void>): Promise<Page> {
  const popupPromise = page.waitForEvent("popup", { timeout: 8_000 }).catch(() => null);
  await action();

  const popup = await popupPromise;
  if (popup) {
    await popup.waitForLoadState("domcontentloaded");
    return popup;
  }

  await page.waitForLoadState("domcontentloaded");
  return page;
}
