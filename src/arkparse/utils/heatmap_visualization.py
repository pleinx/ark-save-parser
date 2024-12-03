from arkparse.enums import ArkMap
from importlib import resources

def draw_heatmap(heatmap, map: ArkMap):
    import matplotlib.pyplot as plt
    import matplotlib.image as mpimg
    import numpy as np

    resolution = len(heatmap)
    mask = heatmap == 0
    with resources.path('arkparse.assets', f'{map.name}.PNG') as img_path:
        img = mpimg.imread(img_path)

    plt.imshow(img, extent=[0, resolution, 0, resolution], aspect='auto', origin='lower')
    plt.colorbar()

    is_all_zero = np.all(heatmap == 0)
    
    if not is_all_zero:
        heatmap_display = plt.imshow(heatmap, cmap='hot', interpolation='nearest', alpha=0.7, vmin=0.1)
        heatmap_display.set_alpha(np.where(mask, 0, 0.7))
    plt.show()