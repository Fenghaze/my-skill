---
name: e2e-testing-automation
description: >
  Build end-to-end automated tests that simulate real user interactions across
  the full application stack. Use for E2E test, Selenium, Cypress, Playwright,
  browser automation, and user journey testing.
  **IMPORTANT: When this skill is triggered, you MUST use the Agent tool to launch
  a sub-agent to execute all E2E test tasks. Never run tests directly in the
  parent agent context — always delegate to a background sub-agent.**
---

# E2E Testing Automation

## Table of Contents

- [Overview](#overview)
- [When to Use](#when-to-use)
- [Execution Mode](#execution-mode)
- [Quick Start](#quick-start)
- [Reference Guides](#reference-guides)
- [Best Practices](#best-practices)

## Overview

End-to-end (E2E) testing validates complete user workflows from the UI through all backend systems, ensuring the entire application stack works together correctly from a user's perspective. E2E tests simulate real user interactions with browsers, handling authentication, navigation, form submissions, and validating results.

## When to Use

- Testing critical user journeys (signup, checkout, login)
- Validating multi-step workflows
- Testing across different browsers and devices
- Regression testing for UI changes
- Verifying frontend-backend integration
- Testing with real user interactions (clicks, typing, scrolling)
- Smoke testing deployments

## Execution Mode

**⚠️ CRITICAL: Always Use Sub-Agents**

When this skill triggers, you MUST execute all E2E test tasks via the `Agent` tool in a background sub-agent. This keeps the parent agent's context clean and prevents test output from consuming context window.

### How to Execute

1. **Analyze** the user's E2E test request
2. **Create** a sub-agent with:
   - `subagent_type`: `general-purpose`
   - `run_in_background`: `true`
   - `prompt`: Include task description, working directory, test commands, and request a summary result
3. **Notify** the user that the test is running in background
4. **Return** the sub-agent's final result when it completes

### Example Sub-Agent Prompt

```
执行以下 E2E 测试任务：

1. 启动目标服务器（如果需要）
2. 运行测试套件：<测试命令>
3. 生成测试报告
4. 返回测试结果摘要

工作目录：<项目路径>

完成后返回测试结果摘要。
```

### When the Sub-Agent Completes

The parent agent will receive a notification with the test results. Relay the summary to the user, including:
- Pass/fail count
- Duration
- Report file path (if generated)

## Quick Start

Minimal working example:

```typescript
// tests/e2e/checkout.spec.ts
import { test, expect, Page } from "@playwright/test";

test.describe("E-commerce Checkout Flow", () => {
  let page: Page;

  test.beforeEach(async ({ page: p }) => {
    page = p;
    await page.goto("/");
  });

  test("complete checkout flow as guest user", async () => {
    // 1. Browse and add product to cart
    await page.click("text=Shop Now");
    await page.click('[data-testid="product-1"]');
    await expect(page.locator("h1")).toContainText("Product Name");

    await page.click('button:has-text("Add to Cart")');
    await expect(page.locator(".cart-count")).toHaveText("1");

    // 2. Go to cart and proceed to checkout
    await page.click('[data-testid="cart-icon"]');
    await expect(page.locator(".cart-item")).toHaveCount(1);
    await page.click("text=Proceed to Checkout");

// ... (see reference guides for full implementation)
```

## Reference Guides

Detailed implementations in the `references/` directory:

| Guide | Contents |
|---|---|
| [Playwright E2E Tests](references/playwright-e2e-tests.md) | Playwright E2E Tests |
| [Cypress E2E Tests](references/cypress-e2e-tests.md) | Cypress E2E Tests |
| [Selenium with Python (pytest)](references/selenium-with-python-pytest.md) | Selenium with Python (pytest) |
| [Page Object Model Pattern](references/page-object-model-pattern.md) | Page Object Model Pattern |

## Best Practices

### ✅ DO

- Use data-testid attributes for stable selectors
- Implement Page Object Model for maintainability
- Test critical user journeys thoroughly
- Run tests in multiple browsers (cross-browser testing)
- Use explicit waits instead of sleep/timeouts
- Clean up test data after each test
- Take screenshots on failures
- Parallelize test execution where possible

### ❌ DON'T

- Use brittle CSS selectors (like nth-child)
- Test every possible UI combination (focus on critical paths)
- Share state between tests
- Use fixed delays (sleep/timeout)
- Ignore flaky tests
- Run E2E tests for unit-level testing
- Test third-party UI components in detail
- Skip mobile/responsive testing
