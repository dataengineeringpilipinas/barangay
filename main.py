from fastapi import FastAPI, HTTPException
from typing import List, Dict, Any
import barangay

app = FastAPI(
    title="Philippines Barangay Explorer API",
    description="Explore Philippines Standard Geographic Code (PSGC) 2025 data",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {
        "message": "Philippines Barangay Explorer API",
        "endpoints": {
            "/regions": "List all regions",
            "/regions/{region_name}/provinces": "List provinces in a region",
            "/regions/{region_name}/provinces/{province_name}/municipalities": "List municipalities in a province",
            "/regions/{region_name}/provinces/{province_name}/municipalities/{municipality_name}/barangays": "List barangays in a municipality",
            "/search/barangay/{barangay_name}": "Search for barangays by name",
            "/stats": "Get statistics about the data"
        }
    }

@app.get("/regions", response_model=List[str])
async def get_regions():
    """Get list of all regions"""
    return list(barangay.BARANGAY.keys())

@app.get("/regions/{region_name}/provinces", response_model=List[str])
async def get_provinces(region_name: str):
    """Get list of provinces in a specific region"""
    if region_name not in barangay.BARANGAY:
        raise HTTPException(status_code=404, detail=f"Region '{region_name}' not found")
    
    return list(barangay.BARANGAY[region_name].keys())

@app.get("/regions/{region_name}/provinces/{province_name}/municipalities", response_model=List[str])
async def get_municipalities(region_name: str, province_name: str):
    """Get list of municipalities in a specific province"""
    if region_name not in barangay.BARANGAY:
        raise HTTPException(status_code=404, detail=f"Region '{region_name}' not found")
    
    if province_name not in barangay.BARANGAY[region_name]:
        raise HTTPException(status_code=404, detail=f"Province '{province_name}' not found in region '{region_name}'")
    
    return list(barangay.BARANGAY[region_name][province_name].keys())

@app.get("/regions/{region_name}/provinces/{province_name}/municipalities/{municipality_name}/barangays", response_model=List[str])
async def get_barangays(region_name: str, province_name: str, municipality_name: str):
    """Get list of barangays in a specific municipality"""
    if region_name not in barangay.BARANGAY:
        raise HTTPException(status_code=404, detail=f"Region '{region_name}' not found")
    
    if province_name not in barangay.BARANGAY[region_name]:
        raise HTTPException(status_code=404, detail=f"Province '{province_name}' not found in region '{region_name}'")
    
    if municipality_name not in barangay.BARANGAY[region_name][province_name]:
        raise HTTPException(status_code=404, detail=f"Municipality '{municipality_name}' not found in province '{province_name}'")
    
    return barangay.BARANGAY[region_name][province_name][municipality_name]

@app.get("/search/barangay/{barangay_name}")
async def search_barangay(barangay_name: str):
    """Search for barangays by name across all regions"""
    results = []
    
    for region_name, provinces in barangay.BARANGAY.items():
        for province_name, municipalities in provinces.items():
            if isinstance(municipalities, dict):
                for municipality_name, barangays in municipalities.items():
                    if isinstance(barangays, list):
                        matching_barangays = [b for b in barangays if barangay_name.lower() in b.lower()]
                        for matching_barangay in matching_barangays:
                            results.append({
                                "barangay": matching_barangay,
                                "municipality": municipality_name,
                                "province": province_name,
                                "region": region_name
                            })
    
    if not results:
        raise HTTPException(status_code=404, detail=f"No barangays found containing '{barangay_name}'")
    
    return {"query": barangay_name, "results": results, "count": len(results)}

@app.get("/stats")
async def get_stats():
    """Get statistics about the PSGC data"""
    total_regions = len(barangay.BARANGAY)
    total_provinces = sum(len(provinces) for provinces in barangay.BARANGAY.values())
    total_municipalities = 0
    total_barangays = 0
    
    for provinces in barangay.BARANGAY.values():
        for municipalities in provinces.values():
            if isinstance(municipalities, dict):
                total_municipalities += len(municipalities)
                for barangays in municipalities.values():
                    if isinstance(barangays, list):
                        total_barangays += len(barangays)
    
    return {
        "total_regions": total_regions,
        "total_provinces": total_provinces,
        "total_municipalities": total_municipalities,
        "total_barangays": total_barangays,
        "data_source": "Philippines Standard Geographic Code (PSGC) 2025"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)