from services.personalization.engine import get_conditioned_range

def attach_personalization(result_item, patient_ctx):
    p = get_conditioned_range(
        test_name=result_item.get("test"),
        value=result_item.get("value"),
        unit=result_item.get("unit"),
        age=patient_ctx.get("age"),
        sex=patient_ctx.get("sex"),
        bmi=patient_ctx.get("bmi"),
        condition=patient_ctx.get("condition")
    )

    result_item["conditioned_range"] = p["conditioned_range"]
    result_item["personalized_status"] = p["status"]
    result_item["personalized_explanation"] = p["personalized_explanation"]

    return result_item
