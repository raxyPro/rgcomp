import os
import urllib.request

# Ensure the output folder exists
os.makedirs("pieces", exist_ok=True)

# List of piece codes
pieces = [
    'wP','wR','wN','wB','wQ','wK',
    'bP','bR','bN','bB','bQ','bK'
]

# Base URL for raw images in the Lichess repo
base_url = "https://raw.githubusercontent.com/lichess-org/lila/master/public/piece/cburnett/{}.png"

for piece in pieces:
    url = base_url.format(piece)
    out_file = os.path.join("pieces", f"{piece}.png")
    try:
        print(f"Downloading {piece} from Lichess: {url}")
        urllib.request.urlretrieve(url, out_file)
    except Exception as e:
        print(f"Failed to download {piece}: {e}")

print("\n✅ All available pieces downloaded (check above for any errors). Place 'pieces/' next to your PGN viewer script.")
