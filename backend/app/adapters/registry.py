from __future__ import annotations

from typing import Any

from app.adapters.base import BaseAdapter
from app.adapters.greenhouse import GreenhouseAdapter
from app.adapters.workday import WorkdayAdapter
from app.adapters.lever import LeverAdapter
from app.adapters.google import GoogleAdapter


class AdapterRegistry:
    """
    Central registry for all CareerOS job-source adapters.

    The rest of the application should not need to know
    which concrete adapter class handles a platform.
    """

    def __init__(
        self,
        adapters: list[BaseAdapter] | None = None,
    ):
        self._adapters: dict[str, BaseAdapter] = {}

        for adapter in adapters or []:
            self.register(adapter)

    def register(
        self,
        adapter: BaseAdapter,
    ) -> None:
        """
        Register an adapter using its platform name.
        """

        name = getattr(
            adapter,
            "name",
            None,
        )

        if not name:
            raise ValueError(
                "Adapter must define a non-empty 'name'"
            )

        normalized_name = str(name).strip().lower()

        if not normalized_name:
            raise ValueError(
                "Adapter name cannot be empty"
            )

        self._adapters[normalized_name] = adapter

    def get(
        self,
        platform: str,
    ) -> BaseAdapter:
        """
        Return the adapter registered for a platform.
        """

        normalized_platform = (
            platform.strip().lower()
            if platform
            else ""
        )

        if not normalized_platform:
            raise ValueError(
                "Company platform is required"
            )

        adapter = self._adapters.get(
            normalized_platform
        )

        if adapter is None:
            supported = ", ".join(
                sorted(self._adapters.keys())
            )

            raise ValueError(
                f"Unsupported platform: "
                f"{platform}. "
                f"Supported platforms: "
                f"{supported or 'none'}"
            )

        return adapter

    def has(
        self,
        platform: str,
    ) -> bool:
        """
        Check whether an adapter exists for a platform.
        """

        if not platform:
            return False

        return (
            platform.strip().lower()
            in self._adapters
        )

    def supported_platforms(self) -> list[str]:
        """
        Return all registered platform names.
        """

        return sorted(
            self._adapters.keys()
        )

    def discover_jobs(
        self,
        company_config: dict[str, Any],
    ):
        """
        Discover jobs using the adapter selected by
        company_config['platform'].
        """

        platform = company_config.get(
            "platform"
        )

        adapter = self.get(platform)

        if not adapter.can_handle(
            company_config
        ):
            raise ValueError(
                f"Adapter '{adapter.name}' "
                f"cannot handle the supplied "
                f"company configuration"
            )

        return adapter.discover_jobs(
            company_config
        )


# --------------------------------------------------
# Default CareerOS registry
# --------------------------------------------------

adapter_registry = AdapterRegistry(
    adapters=[
        GreenhouseAdapter(),
        WorkdayAdapter(),
        LeverAdapter(),
        GoogleAdapter(),
    ]
)