import pytest
from unittest.mock import patch, AsyncMock
from services.notification_service import NotificationService

@patch('services.notification_service.st.toast')
@pytest.mark.asyncio
async def test_asuccess(mock_st_toast):
    # Arrange
    message = "Success message"

    # Act
    await NotificationService.asuccess(message)

    # Assert
    mock_st_toast.assert_called_once_with(message, icon="✅")

@patch('services.notification_service.st.toast')
@pytest.mark.asyncio
async def test_afailure(mock_st_toast):
    # Arrange
    message = "Failure message"

    # Act
    await NotificationService.afailure(message)

    # Assert
    mock_st_toast.assert_called_once_with(message, icon="❌")

@patch('services.notification_service.st.toast', new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_info(mock_st_toast):
    # Arrange
    message = "Info message"

    # Act
    await NotificationService.info(message)

    # Assert
    mock_st_toast.assert_called_once_with(message, icon="ℹ️")

@patch('services.notification_service.st.toast', new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_warning(mock_st_toast):
    # Arrange
    message = "Warning message"

    # Act
    await NotificationService.warning(message)

    # Assert
    mock_st_toast.assert_called_once_with(message, icon="⚠️")

@patch('services.notification_service.st.toast', new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_agreet(mock_st_toast):
    # Arrange
    message = "Greet message"

    # Act
    await NotificationService.agreet(message)

    # Assert
    mock_st_toast.assert_called_once_with(message, icon="👋")
