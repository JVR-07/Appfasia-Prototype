import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from inference_engine.metrics.llm_evaluator import LLMEvaluator, PRIMARY_MODEL, FALLBACK_MODEL


@pytest.fixture
def mock_genai():
    with patch("inference_engine.metrics.llm_evaluator.genai") as mock:
        yield mock


@pytest.fixture
def evaluator(mock_genai):
    # Setup mock models
    generate_content_mock = AsyncMock()
    
    # Configure genai client to return our mock
    client_mock = MagicMock()
    client_mock.aio.models.generate_content = generate_content_mock
    mock_genai.Client.return_value = client_mock
    
    evaluator = LLMEvaluator(api_key="test_key")
    # Attach the mock directly to the evaluator for easy assertions in tests
    evaluator._mock_generate_content = generate_content_mock
    return evaluator


@pytest.mark.asyncio
async def test_evaluate_narration_success(evaluator):
    # Setup the primary model to return a successful JSON string
    mock_response = MagicMock()
    mock_response.text = '{"score_global": 85.0, "dimensions": {"coherencia": 80, "vocabulario": 90}}'
    evaluator._mock_generate_content.return_value = mock_response

    result = await evaluator.evaluate_narration("Habia un perro", "Cuentame del perro", level=2)

    assert result.is_available is True
    assert result.score_global == 85.0
    assert result.dimensions["coherencia"] == 80
    assert result.rubric_type == "narration"
    
    # Check that primary model was called
    evaluator._mock_generate_content.assert_called_once()
    args, kwargs = evaluator._mock_generate_content.call_args
    assert kwargs["model"] == PRIMARY_MODEL


@pytest.mark.asyncio
async def test_evaluate_open_response_success(evaluator):
    mock_response = MagicMock()
    mock_response.text = '{"score_global": 60.0, "dimensions": {"relevancia": 50, "claridad": 70}}'
    evaluator._mock_generate_content.return_value = mock_response

    result = await evaluator.evaluate_open_response("Manzana roja", "De que color es la manzana?", level=1)

    assert result.is_available is True
    assert result.score_global == 60.0
    assert result.dimensions["claridad"] == 70
    assert result.rubric_type == "open_response"


@pytest.mark.asyncio
async def test_fallback_mechanism(evaluator):
    # Primary model throws exception, Fallback returns success
    mock_response = MagicMock()
    mock_response.text = '{"score_global": 75.0, "dimensions": {}}'
    
    evaluator._mock_generate_content.side_effect = [Exception("API rate limit"), mock_response]

    result = await evaluator.evaluate_narration("Test", "Context", level=3)

    assert result.is_available is True
    assert result.score_global == 75.0
    
    assert evaluator._mock_generate_content.call_count == 2
    # Verify the fallback model was requested
    call1_args, call1_kwargs = evaluator._mock_generate_content.call_args_list[0]
    call2_args, call2_kwargs = evaluator._mock_generate_content.call_args_list[1]
    
    assert call1_kwargs["model"] == PRIMARY_MODEL
    assert call2_kwargs["model"] == FALLBACK_MODEL


@pytest.mark.asyncio
async def test_complete_failure_returns_unavailable(evaluator):
    # Both models fail
    evaluator._mock_generate_content.side_effect = [Exception("Fail 1"), Exception("Fail 2")]

    result = await evaluator.evaluate_narration("Test", "Context", level=3)

    assert result.is_available is False
    assert result.score_global == 0.0
    assert result.rubric_type == "narration"
    assert result.dimensions == {}


@pytest.mark.asyncio
async def test_bad_json_returns_unavailable(evaluator):
    # Model returns malformed JSON
    mock_response = MagicMock()
    mock_response.text = '{"score_global": 85.0, missing_quotes_or_something'
    evaluator._mock_generate_content.return_value = mock_response

    result = await evaluator.evaluate_open_response("Test", "Context", level=1)

    assert result.is_available is False
    assert result.score_global == 0.0
