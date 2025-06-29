# fetch_sf_op_v1.py

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import time
import random
import faker

# Initialize Faker for mock data
fake = faker.Faker()
fake.seed_instance(42)

# Initialize FastAPI application
app = FastAPI()

# CORS Configuration
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:1337",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Response data model
class OpportunityData(BaseModel):
    opportunityNumber: str
    proposalName: str
    clientName: str
    value: str
    status: str
    description: str

class APIResponse(BaseModel):
    success: bool
    data: OpportunityData = None
    message: str = None

# Generate 200 mock opportunities
STATUSES = ["New", "Approved", "Draft", "Submitted", "Rejected"]

MOCK_SALESFORCE_DATA = {
    f"OPP{str(i).zfill(3)}": {
        "opportunityNumber": f"OPP{str(i).zfill(3)}",
        "proposalName": fake.bs().title(),
        "clientName": fake.company(),
        "value": f"{random.randint(50000, 500000):.2f}",
        "status": random.choice(STATUSES),
        "description": fake.paragraph(nb_sentences=3)
    }
    for i in range(1, 201)
}

# Endpoint: fetch a single opportunity by number
@app.get("/api/salesforce/opportunity/{opportunity_number}", response_model=APIResponse)
async def get_salesforce_opportunity(opportunity_number: str):
    """
    Fetches a Salesforce opportunity by ID.
    """
    time.sleep(1)  # Simulate network delay
    opportunity_data = MOCK_SALESFORCE_DATA.get(opportunity_number.upper())

    if opportunity_data:
        return APIResponse(success=True, data=OpportunityData(**opportunity_data))
    else:
        return APIResponse(success=False, message="Opportunity number not found.")

# New endpoint: fetch all opportunities (with pagination + filters)
@app.get("/api/salesforce/opportunities", response_model=list[OpportunityData])
async def get_all_salesforce_opportunities(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    client: Optional[str] = None
):
    """
    Returns paginated and filtered Salesforce opportunities.
    - page: which page (default 1)
    - limit: how many per page (default 10)
    - status: filter by status
    - client: partial match on client name
    """
    items = list(MOCK_SALESFORCE_DATA.values())

    if status:
        items = [i for i in items if i["status"].lower() == status.lower()]
    if client:
        items = [i for i in items if client.lower() in i["clientName"].lower()]

    start = (page - 1) * limit
    end = start + limit
    return items[start:end]

# Run locally if executed directly
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
