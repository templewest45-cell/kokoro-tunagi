import cv2
import numpy as np
import os

img_path = "ChatGPT Image 2026年6月21日 15_25_40.png"
out_dir = "cards_output_print"

img = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), cv2.IMREAD_COLOR)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray, (5, 5), 0)
_, thresh = cv2.threshold(blur, 240, 255, cv2.THRESH_BINARY_INV)

contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Find rectangles
cards = []
for cnt in contours:
    area = cv2.contourArea(cnt)
    if area > 20000: # large enough to be a card
        x, y, w, h = cv2.boundingRect(cnt)
        aspect_ratio = float(w)/h
        if 0.5 < aspect_ratio < 0.8: # portrait card
            cards.append((x, y, w, h))

cards.sort(key=lambda b: (b[1]//100, b[0])) # Sort by Y roughly, then X

for i, (x, y, w, h) in enumerate(cards):
    card_img = img[y:y+h, x:x+w]
    is_success, buffer = cv2.imencode(".png", card_img)
    if is_success:
        with open(f"{out_dir}/Action_{i+1}.png", "wb") as f:
            f.write(buffer)
    print(f"Saved Action_{i+1}.png: {w}x{h}")

print(f"Total cards found: {len(cards)}")
