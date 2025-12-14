import cv2
def draw_text_with_bg(frame, text, x, y,
                      font_scale=1,
                      text_color=(255, 255, 255),
                      bg_color=(0, 0, 0),
                      thickness=2):
    """
    Draws text with a solid background rectangle for better visibility
    """

    font = cv2.FONT_HERSHEY_SIMPLEX
    (w, h), _ = cv2.getTextSize(text, font, font_scale, thickness)

    # Draw background rectangle
    cv2.rectangle(
        frame,
        (x - 5, y - h - 10),
        (x + w + 5, y + 5),
        bg_color,
        -1
    )

    # Draw text
    cv2.putText(
        frame,
        text,
        (x, y),
        font,
        font_scale,
        text_color,
        thickness
    )
