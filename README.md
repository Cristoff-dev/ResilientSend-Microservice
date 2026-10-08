# 🚀 ResilientSend-Microservice

> A highly available, fault-tolerant notification gateway built with FastAPI. Designed to protect corporate resources through strict idempotency and ensure message delivery via automatic provider failover.

## 📌 The Problem It Solves
Modern applications rely on external APIs (like Twilio or Resend) for critical communications such as 2FA codes, payment reminders, or welcome emails. When these external services experience downtime or timeouts, businesses lose money and user trust. Furthermore, network retries can lead to duplicate API calls, resulting in double-charging from providers.

**ResilientSend** solves this by acting as a robust middleware that guarantees delivery through fallback strategies while shielding the system from duplicate requests via a serverless Redis cache.

## 🛠️ Architecture & Tech Stack
* **Framework:** FastAPI (Python 3.12+)
* **In-Memory Store:** Upstash Serverless Redis
* **Templating:** Jinja2 (Dynamic HTML rendering)
* **Providers:** Resend (Primary Email), SendGrid (Fallback Email), Twilio (SMS)
* **Design Patterns:** Strategy Pattern, Fail-Open Error Handling, Asynchronous Workers

## ✨ Key Features
1. 🛡️ **Idempotency Engine:** Integrates with Redis to cache successful transactions via an `X-Idempotency-Key` header. Duplicate requests within a 24-hour window are intercepted and neutralized without hitting external APIs, saving costs.
2. 🔄 **Automatic Failover:** Implements the Strategy Pattern. If the primary email provider (Resend) times out or returns a 500 error, the background worker seamlessly switches to the fallback provider (SendGrid) without dropping the payload.
3. ⚡ **Asynchronous Execution:** Heavy HTTP requests and template rendering are delegated to FastAPI `BackgroundTasks`. The API responds instantly with a `202 Accepted`, ensuring the main thread is never blocked.
4. 📱 **Dynamic Omnichannel Routing:** Automatically routes payloads to SMS or Email classes based on a `provider_override` flag in the request body.

## 🧠 Technical Trade-offs & Lessons Learned
Building this microservice required making deliberate architectural decisions to balance reliability with simplicity. Here is the reasoning behind the core design choices:

* **Fail-Open vs. Fail-Closed (The Cache Strategy):** 
  Initially, a failure in the Upstash Redis connection would cause the entire API to throw a `500 Internal Server Error`. I refactored the `IdempotencyManager` to implement a **Fail-Open** strategy. If the serverless cache experiences downtime, the system logs the error but allows the notification to proceed. We temporarily lose duplicate protection, but critical payloads (like 2FA codes) still reach the user. In notification systems, availability beats strict consistency.

* **FastAPI BackgroundTasks vs. Celery/RabbitMQ:** 
  While Celery or message brokers are enterprise standards for background jobs, adding them introduces massive infrastructure complexity and cost. I opted for FastAPI's native `BackgroundTasks`. It strikes the perfect balance: it frees up the main thread to return a `202 Accepted` in milliseconds, while strictly avoiding over-engineering for a standalone microservice.

* **Embracing the Strategy Pattern (SOLID):** 
  It would have been much faster to write a massive `if/elif` block to switch between Resend, SendGrid, and Twilio. I chose the Strategy Pattern to respect the Open/Closed Principle. If a future client requires migrating to AWS SES, I only need to drop in a new `aws_ses.py` class that complies with the `NotificationProvider` interface, completely untouched from the core routing logic.

## 📂 Project Structure
```text
📁 app/
├── 📁 core/
│   ├── config.py             # Environment variables & Pydantic validation
│   └── redis.py              # Upstash Redis connection & Idempotency logic
├── 📁 services/
│   ├── worker.py             # Background task orchestrator
│   └── 📁 notifications/     # Strategy Pattern implementation
│       ├── base.py           # Abstract Base Class
│       ├── email_resend.py   
│       ├── email_sendgrid.py 
│       └── sms_twilio.py     
├── 📁 templates/
│   └── welcome_email.html    # Jinja2 dynamic template
├── main.py                   # FastAPI initialization & CORS
└── routes.py                 # API endpoints
```

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone [https://github.com/your-username/ResilientSend-Microservice.git](https://github.com/your-username/ResilientSend-Microservice.git)
cd ResilientSend-Microservice
```

### 2. Set up the virtual environment
```bash
python -m venv .venv
# On Windows:
.\.venv\Scripts\Activate.ps1
# On macOS/Linux:
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Rename `.env.example` to `.env` and fill in your API keys and Upstash Redis URL.
```env
REDIS_URL="rediss://default:YOUR_PASSWORD@your-region.upstash.io:33221"
RESEND_API_KEY="your_resend_key"
SENDGRID_API_KEY="your_sendgrid_key"
TWILIO_ACCOUNT_SID="your_twilio_sid"
```

### 5. Run the Server
```bash
uvicorn app.main:app --reload
```

## 🧪 API Usage & Testing
Once the server is running, navigate to the auto-generated Swagger UI at `http://localhost:8000/docs` to interact with the API.

### Example Request (POST `/api/v1/notify`)
**Headers:**
`X-Idempotency-Key: unique-transaction-id-12345`

**Body:**
```json
{
  "user_id": "usr_998877",
  "recipient_email": "client@company.com",
  "template_name": "welcome_email",
  "template_data": {
    "name": "Any",
    "verification_code": "845-921",
    "subject": "Your Verification Code"
  }
}
```

### Simulated Failover Test
To trigger the fallback mechanism and observe the system recover automatically, inject `"fail_resend"` into the `subject` property of the `template_data`. Watch the terminal logs as the worker intelligently routes the payload to SendGrid.

---
