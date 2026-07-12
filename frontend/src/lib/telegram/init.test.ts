import { afterEach, describe, expect, it } from "vitest";

import { initTelegram } from "./init";

describe("initTelegram", () => {
  afterEach(() => {
    window.history.replaceState({}, "", "/");
    delete (window as Window & { Telegram?: unknown }).Telegram;
  });

  it("uses raw signed launch data from Telegram's URL fragment", async () => {
    const raw = "auth_date=123&hash=server-verified-later";
    window.history.replaceState(
      {},
      "",
      `/#tgWebAppData=${encodeURIComponent(raw)}&tgWebAppStartParam=share-token`,
    );

    const launch = await initTelegram();

    expect(launch?.initDataRaw).toBe(raw);
    expect(launch?.startParam).toBe("share-token");
  });
});
