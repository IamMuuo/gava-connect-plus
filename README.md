
<p align="center">
  <picture><source media="(prefers-color-scheme: dark)" srcset="https://shieldcn.dev/header/grid.svg?title=gava-connect-plus&amp;subtitle=unofficial+tax+compliance+SDK+for+kenyan+python+devs&amp;logo=python&amp;logoColor=085D37&amp;mode=dark" /><img alt="header" src="https://shieldcn.dev/header/grid.svg?title=gava-connect-plus&amp;subtitle=unofficial+tax+compliance+SDK+for+kenyan+python+devs&amp;logo=python&amp;logoColor=085D37&amp;mode=light" /></picture>
</p>

<p align="center">
  <picture><source media="(prefers-color-scheme: dark)" srcset="https://shieldcn.dev/flag/ke.svg?theme=gray" /><img alt="built in" src="https://shieldcn.dev/flag/ke.svg?theme=gray&amp;mode=light" /></picture>
</p>

# gava-connect-plus

Every Kenyan developer who has built an e-commerce platform, an accounting tool, or a payroll system eventually faces the same formidable milestone: integrating with the Kenya Revenue Authority (KRA) APIs.

Historically, this meant wading through fragmented PDF documentation, wrestling with clunky authentication flows, and writing thousands of lines of fragile boilerplate just to check if a PIN is valid or an eTIMS invoice is authentic. The process wasn't just slow—it was a tax on developer sanity.

gava-connect-plus was born out of a simple, rebellious realization: Integrating with local compliance infrastructure shouldn't feel like standing in a physical KRA line. This library serves as a beautiful, unofficial bridge between modern Python applications and the government gateway—built to handle the heavy lifting of compliance safely, invisibly, and instantly.

## Core Principles

The architecture of gava-connect-plus is guided by three simple truths:


### 1. Developer Zen

The code you write should look like clean Python, not government bureaucracy. Complex SOAP/REST structures, weird payload mappings, and authentication handshakes are abstracted away behind an elegant, predictable API surface. One method call does exactly what it says.

### 2. Radical Isolation

Security is peace of mind. Every corporate department or microservice deserves its own cryptographic boundaries. By keeping service credentials strictly isolated (Invoice, PIN, and Station each running on their own terms), the library prevents permission creep and ensures your production tokens never bleed into one another.

### 3. Execution "Chap Chap"

Time is the only non-renewable asset. Whether running automated testing pipelines in the cloud or deploying to live production, the library is lightweight, optimized, and zero-fluff. It does its job and gets out of your way.


## Installation & Quick Start

True to the principle of execution chap chap, getting the library into your environment takes a single command. We recommend using uv for lightning-fast environment resolution, but standard tools work perfectly too.

```bash
# For the mordenist usinv uv
uv add gava-connect-plus

# The classic way
pip install gava-connect-plus
```


### Obtaining passwords, keys etc

Before writing any code, you need to secure your cryptographic credentials from the official gateway ecosystem.
1. Head over to the Kenyan Government [Developer Portal](https://developer.go.ke/).
2. Register an account and navigate to your dashboard workspace to provision access keys.

> Tutorials for obtaining passwords available on youtube and beyond the scope of this doc

### The Multi-App Architecture (Crucial Note)

The KRA API gateway relies on strict security scoping. Permissions are segregated at the application layer rather than bundled into a single master key. This means credentials must be obtained per module/API.

If your software requires both taxpayer identity verification and invoice tracking, you cannot use a single client key. You must create two separate applications inside the portal:

- App #1: Provisioned explicitly with the `PIN Checker by PIN` scope.
- App #2: Provisioned explicitly with the `Invoice Checker` scope.

Once you have your isolated keys, gava-connect-plus takes complete control of the administrative mess.

**The Promise**: You do not need to worry about the underlying Authorization endpoints, token expiration thresholds, or handshake state machines. Once the library is supplied with your application keys, internal OAuth token provisioning, caching, and background refreshes are executed seamlessly on autopilot.

## 1. Configure the Environment Sanctuary
Expose your isolated sandbox or production credential pairs directly to your system shell thread. The library automatically tracks these exact environment keys, keeping your production secrets completely out of source control:

```bash
# App #1: PIN Validation Credentials
export KRA_PIN_KEY="your_pin_app_consumer_key"
export KRA_PIN_SECRET="your_pin_app_consumer_secret"

# App #2: eTIMS Invoice Credentials
export KRA_INVOICE_KEY="your_invoice_app_consumer_key"
export KRA_INVOICE_SECRET="your_invoice_app_consumer_secret"
```

## 2. Write Pure, Frictionless Python
With your system environments aligned, initialize the workspace context. The library dynamically routes internal token handshakes to their respective apps in the background based on the API you invoke.

```python
from gavaconnect import GavaConnect
from gavaconnect.exceptions import GavaConnectError

# Initialize the engine targeting the KRA gateway sandbox
with GavaConnect(environment="sandbox") as gava:
    try:
        # Validates identity via your PIN-scoped application keys
        record = gava.pin.check("A001234567Z")
        print(f"Identity Verified: {record.taxpayer_name}")
        
        # Audits eTIMS status via your Invoice-scoped application keys
        # All background OAuth tokens swap silently behind the scenes
        invoice = gava.invoice.get("INV-99824-X")
        print(f"Gross Invoice Value: KES {invoice.total_invoice_amount:,.2f}")
        
    except GavaConnectError as e:
        print(f"The gateway returned a peaceful error: {e}")
```

## 3. Explicit Dependency Injection (Alternative)

If you are managing configuration objects programmatically at runtime (e.g., retrieving secrets from an encrypted vault), bypass the environment variables by injecting the multi-app map dictionary directly into the builder constructor:

```python
from gavaconnect import GavaConnect

# Map explicit credentials precisely to their module domain targets
custom_config = {
    "pin": {
        "consumer_key": "vault_pin_key_xyz",
        "consumer_secret": "vault_pin_secret_abc"
    },
    "invoice": {
        "consumer_key": "vault_invoice_key_123",
        "consumer_secret": "vault_invoice_secret_789"
    }
}

with GavaConnect(environment="sandbox", **custom_config) as gava:
    station = gava.station.get("A001234567Z")
    print(f"Assigned Tax Station: {station.station_name}")
```

---

# A word about using the library

## Sync & Async Harmony

Python architectures are diverse. Some systems demand the raw speed of non-blocking concurrency, while others require the rock-solid predictability of standard sequential execution. `gava-connect-plus` honors both paths by providing native, separate engines for both synchronous and asynchronous workflows.

When initializing the library, you can choose the engine that perfectly aligns with your environment constraints and runtime architecture.

### The Asynchronous Path (For High-Concurrence API Gateways)
If you are building high-throughput microservices using modern async frameworks like FastAPI, Litestar, or Sanic, use the async flavor to ensure your application threads never sleep while waiting for network I/O from the KRA gateway:

```python
import asyncio
from gavaconnect import GavaConnect

async def main():
    # Non-blocking connection pooling executing natively inside your event loop
    async with GavaConnectAsync(environment="sandbox") as gava:
        record = await gava.pin.check("A001234567Z")
        print(f"Async Identity Verified: {record.taxpayer_name}")

asyncio.run(main())
```

### The Synchronous Path (For Predictable, Thread-Safe Workflows)

For applications built on standard blocking architectures, the synchronous engine provides a clean, dependency-free wrapper that executes line-by-line without an active event loop loop manager:

```python
from gavaconnect import GavaConnectSync

with GavaConnect(environment="sandbox") as gava:
    record = gava.pin.check("A001234567Z")
    print(f"Sync Identity Verified: {record.taxpayer_name}")

```

### Architectural Nuance: When to stay Synchronous (The Django Paradigm)

It is tempting to default to async for all network utilities, but context dictates performance. For example, if you are integrating this library into a traditional Django application served via a standard WSGI stack (like Gunicorn or uWSGI), you should choose the synchronous version.

The Technical Reason: Django’s core engine, request lifecycle middlewares, and database ORM layers are fundamentally synchronous by design. While Django offers async views, mixing them into a WSGI runtime forces the framework to wrap execution threads in thread-switching utility layers (`async_to_sync` and `sync_to_async`).

If your view is already handling a synchronous database transaction, throwing an asynchronous API call into the middle of it triggers complex context-switching overhead and thread hopping inside the Python runtime. This context switching can actually degrade performance and introduce subtle race conditions with thread-local data. Staying purely synchronous inside a synchronous application architecture keeps your execution path flat, memory overhead minimal, and debugging straightforward.

---

# Path to Completeness (Module Roadmap)
The KRA API ecosystem is vast, covering everything from basic identity checks to complex customs calculations and tax filing routines. Rome wasn't built in a day, and neither is the ultimate developer gateway toolkit.

gava-connect-plus is a living blueprint. While the core verification bedrock is fully operational and production-ready, several advanced transactional modules are currently slated for future integration cycles.

Below is the current state of alignment between the SDK and the official developer.go.ke portal services:



<div align="center">

| Feature / API Endpoint | Status | Tested |
| --- | --- | :---: |
| Automated OAuth Token Lifecycle Management & Caching | ✅ | ✅ |
| PIN Checker by PIN (`PIN_Validation_by_PIN`) | ✅ | ✅ |
| PIN Checker by ID (`DTD_PINChecker`) | ✅ | ✅ |
| Know KRA Tax Service Office/Station (`SUC-iTax-USSD_Know_Your_Station`) | ✅ | ✅ |
| eTIMS Invoice Checker (`Invoice-Checker`) | ✅ | ✅ |
| Fetch Taxpayer Obligations (`TaxPayer_Tax_Obligations_Fetcher`) | ⏳ Planned | - |
| Withholding Tax PRN Generation (Income Tax, Rental, VAT) | ⏳ Planned | - |
| Tax Compliance Certificate (TCC) Validation & Application | ⏳ Planned | - |
| Automated NIL Return Filing (`iTax_NIL_Return`) | ⏳ Planned | - |
| Income Tax & VAT Exemption Checker | ⏳ Planned | - |
| Turnover Tax (TOT) Return Filing | ⏳ Planned | - |
| Customs Declaration Status Checker & Tax Calculator | ⏳ Planned | - |
| Import Certificate Checker (By Number / PIN) | ⏳ Planned | - |
| Individual KRA PIN Registration Gateway | ⏳ Planned | - |
| eTIMS OSCU Integrator Automated Testing Suite | ⏳ Planned | - |
| Excise License Checker (By Pin / Certificate Number) | ⏳ Planned | - |

</div>

# The Genesis & Contributing

Let’s clear the air right away: I am not affiliated, associated, authorized, or in any way officially connected with the Kenya Revenue Authority (KRA). This project was born out of pure, unadulterated developer frustration. While building a commercial product that required KRA portal integrations, I looked around the ecosystem for a robust, production-grade Python package that could handle the gateway safely and seamlessly. I found absolutely nothing.

Faced with a wall of fragmented PDFs and custom network scripts, I decided to take a deep breath, skip a few nights of sleep, and jump straight down the rabbit hole to build the tool that should have already existed. `gava-connect-plus` is the result of that journey.

## Join the Journey
Because this is a community-driven initiative, your hands and minds are needed to help shape it. Whether you want to squash an edge-case bug, optimize the internal caching layers, or drag one of the *Planned transactional* modules into operational reality, contributions are deeply welcomed.

Feel free to open an issue, start a discussion thread, or send a pull request over the wall. Let's make integration painless for the next developer.

## Support the energy
If gava-connect-plus saves you days of digging through portal specifications, keeps your production builds green, or spares your team a minor existential crisis, consider giving back to the project:
- **⭐ Star the Repository**: It costs nothing and directly helps other Kenyan developers discover the project on GitHub.
- **🗣️ Spread the Word**: Share the project link in your local tech WhatsApp groups, Discord servers, or on X (Twitter). Let's build a stronger local open-source culture.
- **☕ Buy Me a Coffee**: If this library saved your business real billable hours, consider fueling the midnight oil for the next sprint of module developments. Your support keeps the zen flowing.

<p align="center">
  <picture><source media="(prefers-color-scheme: dark)" srcset="https://shieldcn.dev/chart/github/stars/iammuuo/gava-connect-plus.svg?theme=green&amp;font=geist&amp;title=Github+stars+over+time&amp;icon=refinedgithub" /><img alt="chart" src="https://shieldcn.dev/chart/github/stars/iammuuo/gava-connect-plus.svg?mode=light&amp;theme=green&amp;font=geist&amp;title=Github+stars+over+time&amp;icon=refinedgithub" /></picture>
</p>
