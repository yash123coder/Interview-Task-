from app.services.lead_classifier import classify_lead


def test_hot_lead_classification():

    lead = {
        "name": "Rahul Sharma",
        "email": "rahul@example.com",
        "phone": "9876543210",
        "company": "ABC Technologies",
        "requirement": (
            "We need an AI-powered lead management "
            "automation solution for our sales team. "
            "We want to implement it within the next month."
        ),
        "budget": 150000,
        "source": "Website"
    }

    result = classify_lead(lead)

    print("\nAI Assessment:")
    print(result.model_dump_json(indent=2))

    assert result.classification in ["HOT", "WARM", "COLD"]
    assert 0.0 <= result.confidence <= 1.0
    assert len(result.reasoning) > 0
    assert len(result.recommended_action) > 0
    assert isinstance(result.missing_information, list)