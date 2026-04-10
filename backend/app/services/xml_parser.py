from lxml import etree


def parse_xml_bytes(raw: bytes) -> etree._Element:
    """Parse XML bytes to an lxml element tree root."""
    return etree.fromstring(raw)


def _local_name_with_prefix(element: etree._Element) -> str:
    """Return element name with namespace prefix (e.g. g:id) instead of full URI."""
    tag = element.tag
    if not isinstance(tag, str) or "{" not in tag:
        return tag

    uri = tag[1 : tag.index("}")]
    local = tag[tag.index("}") + 1 :]

    # Build reverse map from the root's nsmap
    root = element.getroottree().getroot()
    prefix_map = {v: k for k, v in root.nsmap.items() if k is not None}

    prefix = prefix_map.get(uri)
    if prefix:
        return f"{prefix}:{local}"
    return local


def _walk_elements(
    element: etree._Element,
    parent_path: str,
    level: int,
    seen: dict[str, dict],
) -> None:
    """Recursively walk an element tree, collecting element dicts keyed by path."""
    name = _local_name_with_prefix(element)
    path = f"{parent_path}/{name}" if parent_path else name

    children = list(element)
    has_children = len(children) > 0
    text = (element.text or "").strip() if element.text else ""
    is_leaf = not has_children and bool(text)

    if path not in seen:
        seen[path] = {
            "path": path,
            "parent_path": parent_path or None,
            "level": level,
            "element_name": name,
            "value": text if text else None,
            "is_leaf": is_leaf,
            "attribute": False,
        }

    # Process attributes
    for attr_name, attr_value in element.attrib.items():
        attr_display = f"@{attr_name}"
        attr_path = f"{path}/{attr_display}"
        if attr_path not in seen:
            seen[attr_path] = {
                "path": attr_path,
                "parent_path": path,
                "level": level + 1,
                "element_name": attr_display,
                "value": attr_value,
                "is_leaf": True,
                "attribute": True,
            }

    for child in children:
        _walk_elements(child, path, level + 1, seen)


def parse_xml_to_elements(raw: bytes) -> list[dict]:
    """Parse XML bytes into a flat list of element dicts.

    Each dict has: path, parent_path, level, element_name, value, is_leaf, attribute.
    Deduplicates by path (keeps first occurrence as sample).
    Strips namespace URI but keeps prefix (e.g. g:id).
    Detects XML attributes and adds them with @ prefix.
    """
    root = parse_xml_bytes(raw)
    seen: dict[str, dict] = {}
    _walk_elements(root, "", 1, seen)
    return list(seen.values())
