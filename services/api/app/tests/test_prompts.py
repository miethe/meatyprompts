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

def test_list_prompts_with_filters():
    mock_db = MagicMock(spec=Session)
    mock_query = mock_db.query.return_value

    # Simulate the chaining of filter calls
    mock_query.filter.return_value = mock_query

    from app.services.prompt_service import list_prompts
    from app.models.prompt import PromptVersionORM

    list_prompts(mock_db, model="gpt-4", tool="python", purpose="test")

    # Check that query was called on the correct table
    mock_db.query.assert_called_once_with(PromptVersionORM)

    # Check that filter was called for each parameter
    assert mock_query.filter.call_count == 3

    # A more detailed test could inspect the call_args to ensure the
    # correct filter expressions were used, but this is a good start.
