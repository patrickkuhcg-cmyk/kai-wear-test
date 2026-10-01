# Kai Wear — free disposable hosting test

This package hosts the shared Python app, including mobile layout, staff permissions, offline queues and live updates. Python runs on the host, not on your phones.

**Use sample data only. Render Free has no persistent disk. Its local SQLite database, staff accounts, sessions and counter bindings can be erased on sleep, restart or deployment. It is not a durable business database. A reset also invalidates existing offline queues; clear sample browser data before a new test rather than uploading receipts from the previous database. Export sample records before ending a test if you need them.**

## Publish

1. Create or sign in to your GitHub and Render accounts.
2. Create a GitHub repository named `kai-wear-test`. Upload the contents of this folder at the repository root: `server.py`, `hosted_start.py`, `render.yaml`, and the complete `static` folder. Do not upload a live database or any password file.
3. In Render choose **New → Blueprint**, connect that repository and use `render.yaml`. Check the service plan is **Free** before creating it. No paid disk or database is declared in this package.
4. When Render asks for `KAI_OWNER_PASSWORD`, set your own private password of at least 12 characters. Store it in Render's private environment settings, never in GitHub or chat. The username is `owner`.
5. After deployment succeeds, open the exact HTTPS URL displayed by Render. Sign in as owner. Public first-user registration is disabled to prevent someone else claiming ownership.
6. Open **Accounts & access** and create four cashier accounts assigned to Shop 1 Counter 1, Shop 1 Counter 2, Shop 2 Counter 1 and Shop 2 Counter 2. Give each user their own password. Each counter must use one browser installation.
7. Use the same HTTPS address on each phone/computer; leave Chrome's Desktop site option off on phones. Open and sign in online first before offline tests.

The owner password is bootstrapped only on an empty database. Changing it in the app does not change Render's saved environment value; after a database reset, the environment password becomes the initial owner password again.

## Test checklist

- On two separate browsers, sign in as owner and cashier; check one accepted sale updates the owner's totals and stock.
- Connect two cashier browsers to different counters and verify stock decreases independently.
- Disconnect one counter, record a sample sale, reconnect, and check the receipt uploads once.
- Create a viewer and verify write actions are denied.
- Disable a connected cashier and verify access ends; offline revocation only takes effect upon reconnection or grant expiry.
- Check 360px, 390px and desktop layouts. Use the Menu button on phones; wide tables scroll within their panels.

Existing calculation/API tests passed in the original package. The hosted bootstrap is locally smoke-tested; the public host is not deployed or verified until Render returns a successful deployment URL. Keep only fake sales and customers in this test.

Host documentation: https://render.com/docs/free and https://render.com/docs/blueprint-spec
