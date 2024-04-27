import asyncio
import streamlit as st


class NotificationService:
    """
    A class that provides methods for displaying toast notifications with different icons.
    """

    @staticmethod
    def success(message: str):
        """
        Displays a success toast notification with a green checkmark icon.

        Args:
            message (str): The message to display in the toast notification.
        """
        asyncio.run(NotificationService.asuccess(message))

    @staticmethod
    async def asuccess(message: str):
        """
        Displays a success toast notification with a green checkmark icon asynchronously.

        Args:
            message (str): The message to display in the toast notification.
        """
        st.toast(
            message,
            icon="✅",
        )

    @staticmethod
    def failure(message: str):
        """
        Displays a failure toast notification with a red cross icon.

        Args:
            message (str): The message to display in the toast notification.
        """
        asyncio.run(NotificationService.afailure(message))

    @staticmethod
    async def afailure(message: str):
        """
        Displays a failure toast notification with a red cross icon asynchronously.

        Args:
            message (str): The message to display in the toast notification.
        """
        st.toast(
            message,
            icon="❌",
        )

    @staticmethod
    async def info(message: str):
        """
        Displays an informational toast notification with a blue info icon asynchronously.

        Args:
            message (str): The message to display in the toast notification.
        """
        st.toast(
            message,
            icon="ℹ️",
        )

    @staticmethod
    async def warning(message: str):
        """
        Displays a warning toast notification with an orange warning icon asynchronously.

        Args:
            message (str): The message to display in the toast notification.
        """
        st.toast(
            message,
            icon="⚠️",
        )

    @staticmethod
    async def agreet(message: str):
        """
        Displays a greeting toast notification with a waving hand icon asynchronously.

        Args:
            message (str): The message to display in the toast notification.
        """
        st.toast(
            message,
            icon="👋",
        )

    @staticmethod
    def greet(message: str):
        """
        Displays a greeting toast notification with a waving hand icon.

        Args:
            message (str): The message to display in the toast notification.
        """
        asyncio.run(NotificationService.agreet(message))

    @staticmethod
    async def acelebrate(message: str):
        """
        Displays a celebration toast notification with a party popper icon asynchronously.

        Args:
            message (str): The message to display in the toast notification.
        """
        st.toast(
            message,
            icon="🎉",
        )

    @staticmethod
    def celebrate(message: str):
        """
        Displays a celebration toast notification with a party popper icon.

        Args:
            message (str): The message to display in the toast notification.
        """
        asyncio.run(NotificationService.acelebrate(message))
