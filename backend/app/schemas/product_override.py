from pydantic import BaseModel


class ProductOverrideUpsert(BaseModel):
    field_overrides: dict = {}
    excluded: bool = False


class ProductWithOverrideResponse(BaseModel):
    id: int
    product_name: str
    product_value: dict
    override: dict | None
    status: str

    class Config:
        from_attributes = True
