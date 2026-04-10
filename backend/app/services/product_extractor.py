"""Extract product records from XML feed bytes."""

from lxml import etree

# Map well-known namespace URIs to short prefixes.
_NS_PREFIX_MAP: dict[str, str] = {
    "http://base.google.com/ns/1.0": "g",
}


def _local_tag(el: etree._Element) -> str:
    """Return tag with namespace prefix (e.g. ``g:id``) instead of Clark notation."""
    tag: str = el.tag
    if tag.startswith("{"):
        uri, local = tag[1:].split("}", 1)
        prefix = _NS_PREFIX_MAP.get(uri)
        if prefix:
            return f"{prefix}:{local}"
        return local
    return tag


def _element_to_dict(el: etree._Element) -> dict | str:
    """Convert an XML element to a dict.

    * Attributes get ``@`` prefix.
    * Child elements are added recursively.
    * If an element has no children and no attributes it is returned as its text value.
    """
    children = list(el)
    attribs = dict(el.attrib)

    if not children and not attribs:
        return (el.text or "").strip()

    result: dict = {}

    # Attributes with @ prefix
    for attr_name, attr_value in attribs.items():
        result[f"@{attr_name}"] = attr_value

    # Child elements
    for child in children:
        key = _local_tag(child)
        value = _element_to_dict(child)
        result[key] = value

    # If dict has no text-bearing children and the element itself has meaningful
    # text, store it (rare for record-level elements, but handle gracefully).
    text = (el.text or "").strip()
    if text and not children:
        result["#text"] = text

    return result


def _find_record_elements(
    root: etree._Element, record_path: str
) -> list[etree._Element]:
    """Find elements matching *record_path* (e.g. ``feed/entry``) by walking the tree."""
    parts = record_path.strip("/").split("/")
    current: list[etree._Element] = [root]

    # The first part must match the root tag.
    root_tag = _local_tag(root)
    if root_tag != parts[0] and root.tag != parts[0]:
        return []

    for part in parts[1:]:
        next_level: list[etree._Element] = []
        for node in current:
            for child in node:
                if _local_tag(child) == part or child.tag == part:
                    next_level.append(child)
        current = next_level

    return current


def _get_product_name(
    record_el: etree._Element,
    product_name_path: str,
    record_path: str,
) -> str:
    """Extract product name from a record element using *product_name_path*.

    *product_name_path* can be either:
    - absolute (starting with the record_path, e.g. ``feed/entry/title``), or
    - a simple child tag name (e.g. ``title`` or ``name``).
    """
    # Strip record_path prefix if present to get the relative part.
    rel = product_name_path
    record_prefix = record_path.rstrip("/") + "/"
    if rel.startswith(record_prefix):
        rel = rel[len(record_prefix):]

    # Walk the relative path
    parts = rel.strip("/").split("/")
    nodes: list[etree._Element] = [record_el]
    for part in parts:
        next_nodes: list[etree._Element] = []
        for n in nodes:
            for child in n:
                if _local_tag(child) == part or child.tag == part:
                    next_nodes.append(child)
        nodes = next_nodes

    if nodes:
        return (nodes[0].text or "").strip()
    return ""


def extract_products(
    xml_bytes: bytes,
    record_path: str,
    product_name_path: str,
) -> list[dict]:
    """Parse *xml_bytes* and return a list of product dicts.

    Each dict has the shape ``{"product_name": str, "product_value": dict}``.
    """
    root = etree.fromstring(xml_bytes)
    records = _find_record_elements(root, record_path)

    products: list[dict] = []
    for rec in records:
        name = _get_product_name(rec, product_name_path, record_path)
        value = _element_to_dict(rec)
        # value should always be a dict for record-level elements
        if isinstance(value, str):
            value = {"#text": value}
        products.append({"product_name": name, "product_value": value})

    return products
