from app.snipeit import fetch_all_hardware

if __name__ == "__main__":
    for i, hw in enumerate(fetch_all_hardware()):
        if i >= 5:
            break
        print(f"--- Asset #{i+1} ----")
        for k, v in hw.items():
            print(f"{k:20s}: {v!r}")
        print()

