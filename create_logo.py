from PIL import Image, ImageDraw

def create_network_logo(size=(128, 128), output_path="logo.png"):
    """
    Creates a modern, abstract network logo.
    """
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    width, height = size

    # Background
    bg_color = "#1F6AA5"  # Dark blue from the app's theme
    draw.rectangle([0, 0, width, height], fill=bg_color)

    # Network elements
    line_color = "#FFFFFF"
    node_color = "#FFFFFF"
    
    # Draw lines
    draw.line([(width*0.2, height*0.2), (width*0.5, height*0.5)], fill=line_color, width=int(width*0.03))
    draw.line([(width*0.5, height*0.5), (width*0.8, height*0.2)], fill=line_color, width=int(width*0.03))
    draw.line([(width*0.5, height*0.5), (width*0.5, height*0.8)], fill=line_color, width=int(width*0.03))
    draw.line([(width*0.2, height*0.8), (width*0.5, height*0.8)], fill=line_color, width=int(width*0.03))
    draw.line([(width*0.8, height*0.8), (width*0.5, height*0.8)], fill=line_color, width=int(width*0.03))

    # Draw nodes (circles)
    node_radius = int(width * 0.06)
    def draw_node(x, y):
        draw.ellipse([(x-node_radius, y-node_radius), (x+node_radius, y+node_radius)], fill=node_color)

    draw_node(width*0.2, height*0.2)
    draw_node(width*0.8, height*0.2)
    draw_node(width*0.5, height*0.5)
    draw_node(width*0.2, height*0.8)
    draw_node(width*0.5, height*0.8)
    draw_node(width*0.8, height*0.8)

    img.save(output_path)
    print(f"Logo saved to {output_path}")

if __name__ == "__main__":
    create_network_logo()
