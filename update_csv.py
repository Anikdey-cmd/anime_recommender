import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, Polygon, FancyBboxPatch, Circle
import numpy as np

fig, ax = plt.subplots(figsize=(15, 9))
ax.set_xlim(0, 15)
ax.set_ylim(0, 9)
ax.axis('off')

BLUE = "#1F77B4"
RED = "#C0392B"
GREEN = "#2E8B57"
BLACK = "#1a1a1a"
EDGE = "#2c2c2c"

def arrow(x1, y1, x2, y2, lw=1.6):
    a = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='-|>', mutation_scale=16,
                         color=BLACK, lw=lw, zorder=1, shrinkA=0, shrinkB=0)
    ax.add_patch(a)

def rect(x, y, w, h, ec=EDGE, fc="white", lw=1.4):
    r = mpatches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.06",
                                 linewidth=lw, edgecolor=ec, facecolor=fc, zorder=2)
    ax.add_patch(r)

def parallelogram(cx, cy, w, h, skew=0.35, ec=EDGE, fc="white", lw=1.4):
    pts = [
        (cx - w/2 + skew, cy + h/2),
        (cx + w/2 + skew, cy + h/2),
        (cx + w/2 - skew, cy - h/2),
        (cx - w/2 - skew, cy - h/2),
    ]
    p = Polygon(pts, closed=True, edgecolor=ec, facecolor=fc, lw=lw, zorder=2)
    ax.add_patch(p)

def face_icon(cx, cy, r=0.42, skin="#E8B98C", outline=None):
    ax.add_patch(Circle((cx, cy), r, facecolor=skin, edgecolor="#8a6a4a", lw=1.0, zorder=3))
    # simple facial features
    ax.add_patch(Circle((cx-r*0.35, cy+r*0.1), r*0.08, facecolor="#3a2a1a", zorder=4))
    ax.add_patch(Circle((cx+r*0.35, cy+r*0.1), r*0.08, facecolor="#3a2a1a", zorder=4))
    ax.plot([cx-r*0.25, cx+r*0.25], [cy-r*0.35, cy-r*0.35], color="#8a4a3a", lw=1.3, zorder=4)
    if outline == 'lime':
        theta = np.linspace(0, 2*np.pi, 30)
        rr = r*0.75 + 0.05*np.sin(theta*5)
        xs = cx + rr*np.cos(theta)
        ys = cy + rr*np.sin(theta)
        ax.plot(xs, ys, color="#F4D03F", lw=2.0, zorder=5)

def label(x, y, text, fs=13, weight='bold', color=BLACK, ha='center'):
    ax.text(x, y, text, fontsize=fs, fontweight=weight, color=color, ha=ha, va='center')

def multiline(x, y, lines, fs=11, line_gap=0.32, ha='center'):
    n = len(lines)
    start_y = y + (n-1)*line_gap/2
    for i, (text, color, style) in enumerate(lines):
        ax.text(x, start_y - i*line_gap, text, fontsize=fs, color=color,
                 fontweight='bold' if style == 'bold' else 'normal',
                 fontstyle='italic' if style == 'italic' else 'normal', ha=ha, va='center')

# ---------- ROW 1 ----------
y_row1 = 6.6

# Dataset icons
label(1.5, 8.15, "140K Data Set", fs=14)
face_icon(1.0, 7.3, r=0.42)
face_icon(1.7, 7.15, r=0.42)
face_icon(1.35, 6.55, r=0.42)

arrow(2.3, 7.0, 3.05, 7.0)

# Data preprocessing box
label(4.15, 8.15, "Data Preprocessing", fs=14)
rect(3.1, 6.3, 2.1, 1.4, fc="white")
multiline(4.15, 7.0, [
    ("Configuring Data", BLUE, 'bold'),
    ("Folders", BLUE, 'bold'),
    ("Data Augmentation", RED, 'bold'),
], fs=10.5, line_gap=0.34)

arrow(5.25, 7.0, 6.0, 7.0)

# Model training box
label(7.9, 8.6, "Model Training", fs=14)
rect(5.95, 5.35, 3.9, 3.0, fc="white")
multiline(7.9, 6.85, [
    ("InceptionV3 Pre-trained", BLUE, 'italic'),
    ("Model", BLUE, 'italic'),
    ("GlobalAveragePooling2D", BLUE, 'bold'),
    ("Dense with ReLU", BLUE, 'bold'),
    ("BatchNormalization", BLUE, 'bold'),
    ("Dropout", BLUE, 'bold'),
    ("Dense with sigmoid", BLUE, 'bold'),
    ("+", BLACK, 'normal'),
    ("ModelCheckpoint +", GREEN, 'bold'),
    ("EarlyStopping", GREEN, 'bold'),
], fs=9.6, line_gap=0.275)

arrow(9.95, 7.0, 10.7, 7.0)

# Save model parallelogram
label(11.85, 8.15, "Evaluation", fs=14)
parallelogram(11.85, 7.0, 2.1, 1.15, skew=0.3, fc="white")
multiline(11.85, 7.0, [
    ("Save Model", BLACK, 'bold'),
    ("best_model.h5", BLACK, 'bold'),
], fs=10.5, line_gap=0.3)

# down arrow to evaluation parallelogram
arrow(11.85, 6.4, 11.85, 5.55)

parallelogram(11.85, 4.75, 2.1, 1.05, skew=0.3, fc="white")
label(11.85, 4.75, "Evaluation", fs=12, color=BLUE)

# split arrows to Fake / Real
arrow(11.6, 4.2, 11.0, 3.35)
arrow(12.1, 4.2, 12.7, 3.35)
label(10.75, 3.05, "Fake", fs=13)
label(12.95, 3.05, "Real", fs=13)

# ---------- ROW 2 (return path) ----------
y_row2 = 1.9

# arrow from evaluation parallelogram down-left into XAI box
arrow(11.2, 4.35, 8.85, 2.35)

label(7.65, 3.05, "Explainable Artificial", fs=13)
label(7.65, 2.7, "Intelligence", fs=13)
rect(6.55, 1.35, 2.2, 1.15, fc="white")
multiline(7.65, 1.93, [
    ("Saliency", RED, 'bold'),
    ("LIME", BLUE, 'bold'),
], fs=12, line_gap=0.4)

arrow(6.45, 1.93, 5.7, 1.93)

# Explainable output icons
label(2.4, 0.75, "Explainable Output", fs=14)
face_icon(1.75, 1.9, r=0.55)
face_icon(3.0, 1.9, r=0.55, outline='lime')

plt.tight_layout()
plt.savefig('/home/claude/image_branch_workflow.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.savefig('/home/claude/image_branch_workflow.svg', bbox_inches='tight', facecolor='white')
print("done")