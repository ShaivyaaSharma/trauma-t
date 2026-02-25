import uuid
from typing import Dict, Optional

class CheckoutSessionRequest:
    def __init__(self, amount: float, currency: str, success_url: str, cancel_url: str, metadata: Dict):
        self.amount = amount
        self.currency = currency
        self.success_url = success_url
        self.cancel_url = cancel_url
        self.metadata = metadata

class CheckoutSessionResponse:
    def __init__(self, url: str, session_id: str):
        self.url = url
        self.session_id = session_id

class CheckoutStatusResponse:
    def __init__(self, status: str, payment_status: str, amount_total: float, currency: str, metadata: Dict):
        self.status = status
        self.payment_status = payment_status
        self.amount_total = amount_total
        self.currency = currency
        self.metadata = metadata

class StripeCheckout:
    def __init__(self, api_key: str, webhook_url: str):
        self.api_key = api_key
        self.webhook_url = webhook_url

    async def create_checkout_session(self, request: CheckoutSessionRequest) -> CheckoutSessionResponse:
        # Mock implementation for development
        session_id = f"mock_session_{uuid.uuid4().hex}"
        
        # Instead of redirecting to success immediately, we redirect to our new Virtual Gateway page
        # Success URL is passed as a parameter so the gateway knows where to go after "payment"
        import urllib.parse
        frontend_url = request.success_url.split("/payment-success")[0]
        checkout_url = f"{frontend_url}/checkout-mock?session_id={session_id}&success_url={urllib.parse.quote(request.success_url)}"
        
        print(f"MOCK STRIPE: Created session {session_id} for {request.amount} {request.currency}")
        return CheckoutSessionResponse(url=checkout_url, session_id=session_id)

    async def get_checkout_status(self, session_id: str) -> CheckoutStatusResponse:
        # For mock, we always return paid after the redirect
        return CheckoutStatusResponse(
            status="complete", 
            payment_status="paid", 
            amount_total=0.0, 
            currency="inr", 
            metadata={}
        )

    async def handle_webhook(self, body, signature):
        return {"status": "success"}
