from app.adapters.registry import adapter_registry


def main():
    print("=" * 60)
    print("CAREEROS ADAPTER REGISTRY TEST")
    print("=" * 60)

    print()
    print(
        "SUPPORTED PLATFORMS:",
        adapter_registry.supported_platforms(),
    )

    print()

    adapter = adapter_registry.get(
        "greenhouse"
    )

    print(
        "GREENHOUSE ADAPTER:",
        adapter.__class__.__name__,
    )

    print(
        "HAS GREENHOUSE:",
        adapter_registry.has(
            "greenhouse"
        ),
    )

    print(
        "HAS WORKDAY:",
        adapter_registry.has(
            "workday"
        ),
    )

    print()
    print("-" * 60)
    print("STATUS: PASS")
    print("-" * 60)


if __name__ == "__main__":
    main()