from PIL import Image, ImageDraw, ImageEnhance

from app.models.layer import Layer
from app.models.project import Project


def apply_image_adjustments(image: Image.Image, properties: dict) -> Image.Image:
    """Apply image adjustments based on layer properties."""
    if properties.get("contrast", 1.0) != 1.0:
        image = ImageEnhance.Contrast(image).enhance(properties["contrast"])

    if properties.get("brightness", 1.0) != 1.0:
        image = ImageEnhance.Brightness(image).enhance(properties["brightness"])

    if properties.get("sharpness", 1.0) != 1.0:
        image = ImageEnhance.Sharpness(image).enhance(properties["sharpness"])

    return image


def render_image(project: Project, layers: list[Layer]) -> None:
    img = Image.new("RGBA", (project.width, project.height), color=(255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    for layer in layers:
        props = layer.properties

        if layer.type == "rectangle":
            draw.rectangle(
                [
                    (props["x"], props["y"]),
                    (props["x"] + props["width"], props["y"] + props["height"]),
                ],
                fill=props["color"],
                width=0,
            )

        elif layer.type == "circle":
            draw.ellipse(
                [
                    (props["x"] - props["radius"], props["y"] - props["radius"]),
                    (props["x"] + props["radius"], props["y"] + props["radius"]),
                ],
                fill=props["color"],
                width=0,
            )

        elif layer.type == "pen":
            points = [(p["x"], p["y"]) for p in props["points"]]
            if len(points) > 1:
                draw.line(points, fill=props["color"], width=int(props["stroke_width"]))

        elif layer.type == "image":
            try:
                layer_img = Image.open(props["path"])
                layer_img = apply_image_adjustments(layer_img, props)

                if props.get("width") and props.get("height"):
                    layer_img = layer_img.resize(
                        (int(props["width"]), int(props["height"])),
                        Image.Resampling.LANCZOS,
                    )

                img.paste(layer_img, (int(props["x"]), int(props["y"])))
            except (OSError, FileNotFoundError):
                continue

        elif layer.type == "arc":
            bbox = [
                (props["x"] - props["radius"], props["y"] - props["radius"]),
                (props["x"] + props["radius"], props["y"] + props["radius"]),
            ]
            draw.arc(
                bbox,
                start=props["start_angle"],
                end=props["end_angle"],
                fill=props["color"],
                width=int(props["stroke_width"]),
            )

    return img
