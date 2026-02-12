from fastapi import APIRouter, Query, HTTPException, Response, Body
from typing import List
import asyncio
from src.services.fetcher import fetch_subscription
from src.services.merger import merge_clash_configs
from src.models.subscription import Subscription, SubscriptionCreate
from src.services.storage import storage_service

router = APIRouter(
    prefix="/subscription",
    tags=["subscription"],
)

@router.post("/", response_model=Subscription)
async def add_subscription(sub_create: SubscriptionCreate):
    sub = Subscription(**sub_create.model_dump())
    storage_service.add_subscription(sub)
    return sub

@router.delete("/{sub_id}")
async def remove_subscription(sub_id: str):
    storage_service.remove_subscription(sub_id)
    return {"message": "Subscription removed"}

@router.get("/list", response_model=List[Subscription])
async def list_subscriptions():
    return storage_service.get_all_subscriptions()

@router.get("/result")
async def get_merged_result():
    content = storage_service.get_merged_config()
    if not content:
        raise HTTPException(status_code=404, detail="No merged config found. Please add subscriptions and refresh.")
    return Response(
        content=content,
        media_type="application/x-yaml",
        headers={"Content-Disposition": "attachment; filename=merged_clash.yaml"}
    )

@router.post("/refresh")
async def refresh_subscriptions():
    subs = storage_service.get_all_subscriptions()
    if not subs:
        raise HTTPException(status_code=400, detail="No subscriptions to merge")
    
    urls = [s.url for s in subs]
    # Use subscription name if available, else fallback to index-based name
    names = [s.name or f"sub{i}" for i, s in enumerate(subs, 1)]
    
    try:
        # Fetch all subscriptions concurrently
        results = await asyncio.gather(*[fetch_subscription(url) for url in urls], return_exceptions=True)
        
        valid_configs = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Error fetching {urls[i]}: {result}")
                continue
            # Pass tuple of (content, name)
            valid_configs.append((result, names[i]))
            
        if not valid_configs:
            raise HTTPException(status_code=400, detail="Failed to fetch any valid subscriptions")

        # Get custom rules
        custom_rules_text = storage_service.get_custom_rules()
        custom_rules = [r.strip() for r in custom_rules_text.splitlines() if r.strip()]

        merged_yaml = merge_clash_configs(valid_configs, custom_rules=custom_rules)
        storage_service.save_merged_config(merged_yaml)
        
        return {"message": "Refresh successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/merge")
async def merge_subscriptions_direct(urls: List[str] = Query(..., description="List of subscription URLs")):
    try:
        # Fetch all subscriptions concurrently
        results = await asyncio.gather(*[fetch_subscription(url) for url in urls], return_exceptions=True)
        
        valid_configs = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Error fetching {urls[i]}: {result}")
                continue
            # Generate temporary name if ad-hoc merging
            name = f"sub{i+1}"
            valid_configs.append((result, name))
            
        if not valid_configs:
            raise HTTPException(status_code=400, detail="Failed to fetch any valid subscriptions")

        # Get custom rules
        custom_rules_text = storage_service.get_custom_rules()
        custom_rules = [r.strip() for r in custom_rules_text.splitlines() if r.strip()]

        merged_yaml = merge_clash_configs(valid_configs, custom_rules=custom_rules)
        
        return Response(
            content=merged_yaml,
            media_type="application/x-yaml",
            headers={"Content-Disposition": "attachment; filename=merged_clash.yaml"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

