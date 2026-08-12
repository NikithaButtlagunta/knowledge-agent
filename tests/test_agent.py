import pytest
from unittest.mock import AsyncMock, patch

from backend.app.agents.test_agent import ask_model


@pytest.mark.asyncio
async def test_ask_model_returns_response_content():
    mock_response = type(
        "MockResponse",
        (),
        {"content": "Test response"}
    )()

    with patch(
        "backend.app.agents.test_agent.model",
        autospec=True
    ) as mock_model:

        mock_model.ainvoke = AsyncMock(
            return_value=mock_response
        )

        result = await ask_model("What is a test?")

    assert result == "Test response"