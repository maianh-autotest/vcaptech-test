import { test } from "@playwright/test";
import { RocportalLoginPage } from "../pages/rocportal-login.page";
import { RocscienceHomePage } from "../pages/rocscience-home.page";

test("should navigate to RocPortal login page with required controls visible", async ({ page }) => {
  const homePage = new RocscienceHomePage(page);
  await homePage.open();

  const loginContextPage = await homePage.openRocportalLoginPage();
  const loginPage = new RocportalLoginPage(loginContextPage);

  await loginPage.assertLoaded();
  await loginPage.assertRequiredControlsVisible();
});
