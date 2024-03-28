import asyncio
import streamlit as st


class NotificationService:
    @staticmethod
    def success(message: str):
        asyncio.run(NotificationService.asuccess(message))

    @staticmethod
    async def asuccess(message: str):
        # Use a green checkmark icon for success messages
        st.toast(
            message,
            icon="✅",
        )

    @staticmethod
    def failure(message: str):
        asyncio.run(NotificationService.afailure(message))

    @staticmethod
    async def afailure(message: str):
        # Use a red cross icon for failure messages
        st.toast(
            message,
            icon="❌",
        )

    @staticmethod
    async def info(message: str):
        # Use a blue info icon for informational messages
        st.toast(
            message,
            icon="ℹ️",
        )

    @staticmethod
    async def warning(message: str):
        # Use an orange warning icon for warnings
        st.toast(
            message,
            icon="⚠️",
        )
