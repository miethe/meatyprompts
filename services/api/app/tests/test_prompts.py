from app.services.prompt_service import create_prompt
from app.models.prompt import PromptCreate
from sqlalchemy.orm import Session
from unittest.mock import MagicMock

def test_create_prompt():
    mock_db = MagicMock(spec=Session)
    prompt_data = PromptCreate(
        title="Test Prompt",
        body="This is a test prompt.",
        models=["gpt-3.5-turbo"],
    )

    prompt = create_prompt(db=mock_db, prompt=prompt_data)

    assert prompt.title == "Test Prompt"
    assert prompt.version == 1
    assert mock_db.add.call_count == 2
    assert mock_db.commit.call_count == 3
    assert mock_db.refresh.call_count == 2
