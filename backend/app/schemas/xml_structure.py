from pydantic import BaseModel


class StructureElementIn(BaseModel):
    sort_key: str
    custom_element: bool = False
    path_in: str | None = None
    level_out: int
    path_out: str
    parent_path_out: str | None = None
    element_name_out: str
    is_leaf: bool = False
    attribute: bool = False


class StructureElementResponse(BaseModel):
    id: int
    sort_key: str
    custom_element: bool
    path_in: str | None = None
    level_out: int
    path_out: str
    parent_path_out: str | None = None
    element_name_out: str
    is_leaf: bool
    attribute: bool

    model_config = {"from_attributes": True}
