from sqlalchemy import text

from app.models import Plan, User, FeedIn, XmlElementIn, ProductIn, FeedOut, XmlStructureOut


def test_plan_table_exists(db_session):
    result = db_session.execute(text("SELECT * FROM auth.plans ORDER BY id"))
    plans = result.fetchall()
    assert len(plans) == 4

    free_plan = plans[0]
    assert free_plan.name == "Free"
    assert free_plan.max_products == 200
    assert free_plan.max_feeds_out == 1


def test_all_models_have_correct_tablenames():
    expected = {
        Plan: "plans",
        User: "users",
        FeedIn: "feed_in",
        XmlElementIn: "xml_element_in",
        ProductIn: "product_in",
        FeedOut: "feed_out",
        XmlStructureOut: "xml_structure_out",
    }
    for model, tablename in expected.items():
        assert model.__tablename__ == tablename, (
            f"{model.__name__}.__tablename__ should be '{tablename}'"
        )
